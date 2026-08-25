"""Fill the ETF master-thesis topic registration form (Master_rad_Obrazlozenje_formular.docx).

The template marks every field to be completed in red (FF0000); this replaces those runs with
black body text, keeping the faculty letterhead, styles, and paragraph properties intact.
"""
import re
import shutil
import sys
import zipfile
from pathlib import Path
from xml.sax.saxutils import escape

HERE = Path(__file__).resolve().parent
TEMPLATE = HERE / "formular.docx"
OUTPUT = HERE / "Obrazlozenje_teme_Vuk_Djordjevic.docx"

STUDENT = "Вук Ђорђевић"
INDEX = "2024 / 3102"
MODUL = "Рачунарска техника и информатика"
TITLE_SR = "Хибридно осветљење у реалном времену применом праћења зрака"
TITLE_EN = "Real-Time Hybrid Lighting Using Ray Tracing"
DATE_ONLY = "25. 08. 2026."

PREDMET = [
    "Приказ тродимензионалних сцена у реалном времену ослања се на растеризацију, која одређује шта "
    "је непосредно видљиво из камере, али не и шта се види из саме тачке на површини. Од тог "
    "одговора зависе меке сенке, затамњење у угловима и пукотинама, одрази и посредно осветљење "
    "које се одбија између површина. Ти ефекти се деценијама приближно рачунају поступцима у "
    "простору екрана или унапред израчунатим поступцима, који не прате покретну геометрију.",
    "Наменске хардверске јединице учиниле су праћење зрака кроз целу сцену изводљивим у "
    "интерактивном темпу, али је потпуно решавање једначине приказа и даље прескупо, а мали број "
    "зрака по пикселу производи изражен шум. Практичан приступ је зато хибридни: непосредна "
    "видљивост се растеризује, а посредне појаве се додају као пролази са праћењем зрака и малим "
    "бројем узорака, уз накнадну реконструкцију слике. Тај приступ је основа савремених "
    "комерцијалних система приказа, али се поштено поређење цене појединачних појава на хардверу "
    "различитих произвођача, над истим кодом, у литератури ретко среће.",
]

CILJ = [
    "Циљ рада је развој и експериментална анализа хибридног система осветљења у реалном времену "
    "изнад система приказа који је аутор самостално написао. Сенке, затамњење услед заклоњености, "
    "одрази и дифузно посредно осветљење реализују се праћењем зрака изнад растеризационог пролаза, "
    "а шум који настаје малим бројем узорака уклања се заједничким филтром за реконструкцију и "
    "временским усредњавањем слике.",
    "Мерљиви исходи су три: цена сваке појаве у милисекундама на графичком процесору, зависност "
    "квалитета реконструкције од броја зрака по пикселу, и понашање истог решења на процесорима два "
    "произвођача. Обим је ограничен на једну класу сцене, дифузно посредно осветљење и два уређаја "
    "актуелне генерације, чиме рад остаје изводљив у предвиђеном року.",
]

METODOLOGIJA = [
    "Истраживање је експериментално и почива на поновљивим мерењима. Цена сваке појаве изолује се "
    "низом конфигурација у којима се укључује тачно једна нова појава, па је разлика у времену "
    "између суседних конфигурација њена цена; време се мери временским жиговима на графичком "
    "процесору и усредњава преко задатог броја кадрова.",
    "Квалитет се мери у односу на конвергирану референцу добијену праћењем путање зрака, "
    "перцептивном мером разлике слика и класичним мерама сличности, усредњено преко више тачака "
    "гледишта. Поређење произвођача изводи се покретањем истог програма и истих шејдера на оба "
    "уређаја, чиме се разлика приписује хардверу и управљачком програму. Мерења покреће скриптовано "
    "окружење које резултате упоређује са раније сачуваним вредностима.",
    "Алати: програмски језик C++, интерфејс Vulkan са проширењима за праћење зрака, језик HLSL "
    "преведен у међукод SPIR-V, и језик Python за мерно окружење.",
]

SADRZAJ_MAP = [
    "Реализација обухвата четири појаве осветљења и филтар за реконструкцију слике.",
]

DOPRINOSI = [
    "1. Обједињена реализација четири појаве осветљења засноване на праћењу зрака, под слободном лиценцом.",
    "2. Расподела цене по појави у времену на графичком процесору, из поновљивог упоредног мерења.",
    "3. Оцена филтра за уклањање шума дељеног између четири сигнала: квалитет, цена и стабилност.",
    "4. Поређење идентичног кода на графичким процесорима два произвођача, ретко изведено у литератури.",
    "5. Поновно употребљив образац рачунања у половичној резолуцији уз накнадно повећање резолуције.",
]



def para(text, pPr, bold=False, size="24"):
    """One body paragraph carrying the template's paragraph properties but black, unmarked text."""
    b = "<w:b/>" if bold else ""
    rpr = (f'<w:rPr>{b}<w:sz w:val="{size}"/><w:szCs w:val="{size}"/>'
           f'<w:lang w:val="sr-Cyrl-RS"/></w:rPr>')
    return (f'<w:p><w:pPr>{pPr}</w:pPr><w:r>{rpr}'
            f'<w:t xml:space="preserve">{escape(text)}</w:t></w:r></w:p>')


def merge_runs(xml: str) -> str:
    """Coalesce adjacent runs that share identical properties.

    Word splits a visible phrase across many <w:r> elements (revision ids, spell-check state), so a
    string you can see in the document often does not exist contiguously in the XML. Merging first is
    what makes the placeholder text findable. Done here rather than with an external helper so the
    script has no dependency beyond the standard library.
    """
    pattern = re.compile(
        r"<w:r>(<w:rPr>.*?</w:rPr>)?(<w:t(?: xml:space=\"preserve\")?>)(.*?)(</w:t>)</w:r>"
        r"<w:r>(<w:rPr>.*?</w:rPr>)?<w:t(?: xml:space=\"preserve\")?>(.*?)</w:t></w:r>",
        re.S)

    def join(m):
        rpr_a, open_t, text_a, close_t, rpr_b, text_b = m.groups()
        if (rpr_a or "") != (rpr_b or ""):
            return m.group(0)
        return f"<w:r>{rpr_a or ''}<w:t xml:space=\"preserve\">{text_a}{text_b}</w:t></w:r>"

    for _ in range(40):
        merged = pattern.sub(join, xml)
        if merged == xml:
            break
        xml = merged
    return xml


def fill(xml: str) -> str:
    xml = merge_runs(xml)
    paras = re.findall(r"<w:p[ >].*?</w:p>", xml, re.S)

    def ppr_of(i):
        m = re.search(r"<w:pPr>(.*?)</w:pPr>", paras[i], re.S)
        if not m:
            return '<w:pStyle w:val="Tekstmemoranduma"/><w:ind w:left="0"/>'
        return re.sub(r"<w:rPr>.*?</w:rPr>", "", m.group(1), flags=re.S)

    repl = {
        3: para(STUDENT, ppr_of(3)),
        5: para(INDEX, ppr_of(5)),
        7: para(MODUL, ppr_of(7)),
        10: para(TITLE_SR, ppr_of(10), bold=True),
        12: para(TITLE_EN, ppr_of(12), bold=True),
        14: "".join(para(t, ppr_of(14)) for t in PREDMET),
        16: "".join(para(t, ppr_of(16)) for t in CILJ),
        18: "".join(para(t, ppr_of(18)) for t in METODOLOGIJA),
        # prose, not a seventh chapter, so it must not inherit the bullet list above it
        26: paras[26] + "".join(para(t, ppr_of(14)) for t in SADRZAJ_MAP),
        28: "".join(para(t, ppr_of(28)) for t in DOPRINOSI),
    }

    # The trailing "Напомене" block is guidance to whoever fills the form, not part of what is
    # submitted, and dropping it is also what makes the two-page limit it states achievable.
    for i, p in enumerate(paras):
        if "Напомене" in p:
            repl[i] = ""

    for i, new in sorted(repl.items(), reverse=True):
        xml = xml.replace(paras[i], new, 1)

    before = xml
    xml = xml.replace("ХХ. ХХ. 202х.", escape(DATE_ONLY))
    if xml == before:
        print("WARNING: date placeholder not found, check the signature line")

    # That run is red as EE0000 rather than the FF0000 the rest of the template uses, so it survives
    # a naive colour sweep; recolour it to match the surrounding black text.
    # The run may carry attributes (<w:r w:rsidRPr="...">), so do not anchor on a bare <w:r>.
    xml = re.sub(
        r'(<w:r\b[^>]*>(?:(?!</w:r>).)*?)<w:color w:val="EE0000"/>'
        r'((?:(?!</w:r>).)*?' + re.escape(escape(DATE_ONLY)) + r')',
        r"\1\2", xml, flags=re.S)

    # Removing the guidance block leaves empty paragraphs that Word still paginates, producing a
    # blank third page carrying only the letterhead.
    tail = re.search(r"(?s)(.*)(<w:sectPr\b.*)$", xml)
    if tail:
        body, sect = tail.group(1), tail.group(2)
        while True:
            m = re.search(r"<w:p\b(?:(?!</w:p>).)*?/>\s*$|<w:p\b(?:(?!<w:t).)*?</w:p>\s*$", body, re.S)
            if not m:
                break
            body = body[: m.start()]
        xml = body + sect

    return xml


def main() -> int:
    if not TEMPLATE.exists():
        print(f"FAIL: template not found at {TEMPLATE}")
        return 1

    tmp = HERE / ".build"
    shutil.rmtree(tmp, ignore_errors=True)
    tmp.mkdir()
    with zipfile.ZipFile(TEMPLATE) as z:
        names = [n for n in z.namelist() if not n.startswith("/") and ".." not in n]
        z.extractall(tmp, members=names)

    doc = tmp / "word" / "document.xml"
    xml = fill(doc.read_text(encoding="utf-8"))
    doc.write_text(xml, encoding="utf-8")

    # The template uses two different reds; check both, or the sweep reports a false all-clear.
    left = sum(xml.count(c) for c in ("FF0000", "EE0000"))

    if OUTPUT.exists():
        OUTPUT.unlink()
    with zipfile.ZipFile(OUTPUT, "w", zipfile.ZIP_DEFLATED) as z:
        for f in sorted(tmp.rglob("*")):
            if f.is_file():
                z.write(f, f.relative_to(tmp).as_posix())
    shutil.rmtree(tmp, ignore_errors=True)

    print(f"wrote {OUTPUT.name}  (unfilled red runs remaining: {left})")
    return 0 if left == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
