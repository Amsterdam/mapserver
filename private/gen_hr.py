import re
import random

from generate import block, header, p, q


def slugify(s: str) -> str:
    # TODO would be cleaner to convert to NFD, then remove combining chars.
    s = s.replace("ë", "e")
    return re.sub(r"[^A-Za-z]+", "_", s).strip("_").lower()

def random_colorpicker ():
    min = 0
    max = 255
    red = random.randint(min, max) 
    green = random.randint(min, max) 
    blue = random.randint(min, max) 
    
    return f'{red} {green} {blue}'


# From https://www.amsterdam.nl/stelselpedia/hr-index/catalogus-hr/domeinen/sbi-code/.
sbi = {
    "A Landbouw, bosbouw en visserij":
        [
        ("01", "Landbouw, jacht en dienstverlening voor de landbouw en jacht"),
        ("02", "Bosbouw, exploitatie van bossen en dienstverlening voor de bosbouw"),
        ("03", "Visserij en kweken van vis en schaaldieren")
        ],
    "B Winning van delfstoffen":
        [
        ("06", "Winning van aardolie en aardgas"),
        ("08", "Winning van delfstoffen (geen olie en gas)"),
        ("09", "Dienstverlening voor de winning van delfstoffen")
        ],
    "C Industrie":
        [
        ("10", "Vervaardiging van voedingsmiddelen"),
        ("11", "Vervaardiging van dranken"),
        ("12", "Vervaardiging van tabaksproducten"),
        ("13", "Vervaardiging van textiel"),
        ("14", "Vervaardiging van kleding"),
        ("15", "Vervaardiging van leer, lederwaren en schoenen"),
        ("16","Primaire houtbewerking en vervaardiging van artikelen van hout, kurk, riet en vlechtwerk (geen meubels)"),
        ("17", "Vervaardiging van papier, karton en papier- en kartonwaren"),
        ("18", "Drukkerijen, reproductie van opgenomen media"),
        ("19", "Vervaardiging van cokesovenproducten en aardolieverwerking"),
        ("20", "Vervaardiging van chemische producten"),
        ("21", "Vervaardiging van farmaceutische grondstoffen en producten"),
        ("22", "Vervaardiging van producten van rubber en kunststof"),
        ("23", "Vervaardiging van overige niet-metaalhoudende minerale producten"),
        ("24", "Vervaardiging van metalen in primaire vorm"),
        ("25", "Vervaardiging van producten van metaal (geen machines en apparaten)"),
        ("26", "Vervaardiging van computers en van elektronische en optische apparatuur"),
        ("27", "Vervaardiging van elektrische apparatuur"),
        ("28", "Vervaardiging van overige machines en apparaten"),
        ("29", "Vervaardiging van auto’s, aanhangwagens en opleggers"),
        ("30", "Vervaardiging van overige transportmiddelen"),
        ("31", "Vervaardiging van meubels"),
        ("32", "Vervaardiging van overige goederen"),
        ("33", "Reparatie en installatie van machines en apparaten")
        ],
    "D Productie en distributie van en handel in elektriciteit, aardgas, stoom en gekoelde lucht":
        [
        ("35","Productie en distributie van en handel in elektriciteit, aardgas, stoom en gekoelde lucht")
        ],
    "E Winning en distributie van water; afval- en afvalwaterbeheer en sanering":
        [
        ("36", "Winning en distributie van water"),
        ("37", "Afvalwaterinzameling en -behandeling"),
        ("38", "Afvalinzameling en -behandeling; voorbereiding tot recycling"),
        ("39", "Sanering en overig afvalbeheer")
        ],
    "F Bouwnijverheid":
        [  
        ("41", "Algemene burgerlijke en utiliteitsbouw en projectontwikkeling"),
        ("42", "Grond-, water- en wegenbouw (geen grondverzet)"),
        ("43", "Gespecialiseerde werkzaamheden in de bouw")
        ],
    "G Groot- en detailhandel; reparatie van auto’s":
        [
        ("45", "Handel in en reparatie van auto’s, motorfietsen en aanhangers"),
        ("46", "Groothandel en handelsbemiddeling (niet in auto’s en motorfietsen)"),
        ("47", "Detailhandel (niet in auto’s)")
        ],
    "H Vervoer en opslag":
        [         
        ("49", "Vervoer over land"),
        ("50", "Vervoer over water"),
        ("51", "Luchtvaart"),
        ("52", "Opslag en dienstverlening voor vervoer"),
        ("53", "Post en koeriers")
        ],
    "I Logies-, maaltijd- en drankverstrekking":
        [       
        ("55", "Logiesverstrekking"),
        ("56", "Eet- en drinkgelegenheden")
        ],
    "J Informatie en communicatie":
        [
        ("58", "Uitgeverijen"),
        ("59","Productie en distributie van films en televisieprogramma´s; maken en uitgeven van geluidsopnamen",
        ),
        ("60", "Verzorgen en uitzenden van radio- en televisieprogramma’s"),
        ("61", "Telecommunicatie"),
        ("62", "Dienstverlenende activiteiten op het gebied van informatietechnologie"),
        ("63", "Dienstverlenende activiteiten op het gebied van informatie")
        ],
    "K Financiële instellingen":
        [
        ("64", "Financiële instellingen (geen verzekeringen en pensioenfondsen)"),
        ("65", "Verzekeringen en pensioenfondsen (geen verplichte sociale verzekeringen)"),
        ("66", "Overige financiële dienstverlening")
        ],
    "L Verhuur van en handel in onroerend goed":
        [
        ("68", "Verhuur van en handel in onroerend goed")
        ],
    "M Advisering, onderzoek en overige specialistische zakelijke dienstverlening":
        [
        ("69","Rechtskundige dienstverlening, accountancy, belastingadvisering en administratie"),
        ("70","Holdings (geen financiële), concerndiensten binnen eigen concern en managementadvisering"),
        ("71","Architecten, ingenieurs en technisch ontwerp en advies; keuring en controle"),
        ("72", "Speur- en ontwikkelingswerk"),
        ("73", "Reclame en marktonderzoek"),
        ("74","Industrieel ontwerp en vormgeving, fotografie, vertaling en overige consultancy"),
        ("75", "Veterinaire dienstverlening")
        ],
    "N Verhuur van roerende goederen en overige zakelijke dienstverlening":
        [
        ("77","Verhuur en lease van auto’s, consumentenartikelen, machines en overige roerende goederen"),
        ("78", "Arbeidsbemiddeling, uitzendbureaus en personeelsbeheer"),
        ("79", "Reisbemiddeling, reisorganisatie, toeristische informatie en reserveringsbureaus"),
        ("80", "Beveiliging en opsporing"),
        ("81", "Facility management, reiniging en landschapsverzorging"),
        ("82", "Overige zakelijke dienstverlening")
        ],
    "O Openbaar bestuur, overheidsdiensten en verplichte sociale verzekeringen":
        [
        ("84", "Openbaar bestuur, overheidsdiensten en verplichte sociale verzekeringen")
        ],
    "P Onderwijs": 
        [
        ("85", "Onderwijs")
        ],
    "Q Gezondheids- en welzijnszorg":
        [
        ("86", "Gezondheidszorg"),
        ("87", "Verpleging, verzorging en begeleiding met overnachting"),
        ("88", "Maatschappelijke dienstverlening zonder overnachting")
        ],
    "R Cultuur, sport en recreatie":
        [
        ("90", "Kunst"),
        ("91","Culturele uitleencentra, openbare archieven, musea, dieren- en plantentuinen, natuurbehoud"),
        ("92", "Loterijen en kansspelen"),
        ("93", "Sport en recreatie")
        ],
    "S Overige dienstverlening":
        [
        ("94", "Levensbeschouwelijke en politieke organisaties, belangen- en ideële organisaties, hobbyclubs"),
        ("95", "Reparatie van computers en consumentenartikelen"),
        ("96", "Wellness en overige dienstverlening; uitvaartbranche")
        ],
    "T Huishoudens als werkgever; niet-gedifferentieerde productie van goederen en diensten door huishoudens voor eigen gebruik":
        [
        ("97", "Huishoudens als werkgever van huishoudelijk personeel"),
        ("98","Niet-gespecificeerde productie van goederen en diensten door particuliere huishoudens voor eigen gebruik")
        ],
    "U Extraterritoriale organisaties en lichamen":
    [
    ("99", "Extraterritoriale organisaties en lichamen")
    ],
}

#header(team="BenK")

with block("MAP"):
    p("NAME", "Handelsregister")
    p("INCLUDE", "header.inc")

    p("DEBUG 5")

    with block("WEB"):
        with block("METADATA"):
            q("ows_title", "Handelsregister")
            q("ows_abstract", "Vestigingen in de gemeente Amsterdam uit het Handelsregister",)

    with block("LEGEND"):
        p("STATUS ON")
        p("KEYSIZE 16 16")
    
    for group in sbi:
        for code, descr in sbi[group]:
            sql = f"""
                SELECT
                    naam, vestigingsnummer, bezoek_geopunt, sbi_code, omschrijving
                FROM
                    hr_ves hv
                    INNER JOIN hr_ves_activiteiten hva
                    ON hva.parent_id = hv.vestigingsnummer
                WHERE
                    bezoek_geopunt IS NOT NULL
                    AND is_hoofdactiviteit = 'Ja'
                    AND substring(sbi_code FROM 1 FOR 2) = {code!r}
            """

            sql = " ".join(sql.split())  # Normalize whitespace.
            sql = (
                f"bezoek_geopunt FROM ({sql}) AS sub"
                + " USING srid=28992 USING UNIQUE vestigingsnummer"
            )
            slug = slugify(descr)

            with block("LAYER"):
                p("NAME", slug)
                p("GROUP", group)
                p("INCLUDE", "connection/dataservices.inc")
                p("DATA", sql)
                p("TYPE POINT")
                # p("MINSCALEDENOM 10")
                # p("MAXSCALEDENOM 9001")
                p("TEMPLATE", "fooOnlyForWMSGetFeatureInfo.html")
                p("PROCESSING", "CLOSE_CONNECTION=DEFER")
                p("STATUS OFF")

                with block("PROJECTION"):
                    q("init=epsg:28992")

                with block("METADATA"):
                    q("ows_title", slug)
                    q("ows_group_title", group)
                    q("ows_abstract", "Vestigingen van: " + descr)
                    q("gml_include_items", "all")

                # TODO multiple classes

                with block("CLASS"):
                    with block("STYLE"):
                        p("SYMBOL", "stip")
                        p("SIZE 16")
                        p(f"COLOR {random_colorpicker()}")
                        p('OUTLINECOLOR 0 0 0')
                        p ('WIDTH 5')


            with block("LAYER"):
                p("NAME", slug + "_label")
                p("GROUP", group)
                p("INCLUDE", "connection/dataservices.inc")
                p("DATA", sql)
                p("TYPE POINT")
                # p("MINSCALEDENOM 100")
                # p("MAXSCALEDENOM 1001")
                p("TEMPLATE", "fooOnlyForWMSGetFeatureInfo.html")
                p("PROCESSING", "CLOSE_CONNECTION=DEFER")
                p("STATUS OFF")

                with block("PROJECTION"):
                    q("init=epsg:28992")

                with block("METADATA"):
                    q("ows_title", slug + "_label")
                    q("ows_group_title", "vestigingen_cbs_label")
                    q("ows_abstract", "Labels van vestigingen")

                p("LABELITEM", "naam")

                with block("CLASS"):
                    with block("LABEL"):
                        # p("MINSCALEDENOM 100")
                        # p("MAXSCALEDENOM 1001")
                        p("COLOR 0 0 0")
                        p("OUTLINECOLOR 255 255 255")
                        p("OUTLINEWIDTH 3")
                        p("FONT", "Ubuntu-M")
                        p("TYPE truetype")
                        p("SIZE 10")
                        p("POSITION AUTO")
                        p("PARTIALS FALSE")
                        p("OFFSET -60 10")
