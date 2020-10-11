TH1 = 4
TH2 = 30
TH_LEFT_GROUPING = 10
SIZES_PX = {1: "10px", 2: "13px", 3: "16px", 4: "18px", 5: "24px", 6: "32px", 7: "48px"}
SIZES_PCT = {-7: "30%", -6: "40%", -5: "50%", -4: "60%", -3: "70%", -2: "80%", -1: "90%", 0: "100%", 1: "110%", 2: "120%", 3: "130%", 4: "140%", 5: "150%", 6: "160%", 7: "170%", }
DEFAULT_STYLE = """
body{
  font-weight: normal;
  font-style: normal;
  font-size: 16px;
  line-height: 12px;
  line-height: 19px;
  display: block;
  margin-top: 8px;
  margin-bottom: 8px;
  margin-left: 8px;
  margin-right: 8px;
  padding-top: 0px;
  padding-bottom: 0px;
  padding-left: 0px;
  padding-right: 0px;
  color: #000000;
  text-align: left;
  text-indent: 0px;
}
p{
  margin-top: 16px;
  margin-bottom: 16px;
  margin-left: 0px;
  margin-right: 0px;
  display: block;
  text-indent: 0px;
}
*{
  display: inline;
}
body, address, dir, table, center, li, tr, td, hr, blockquote, h1, h2, h3, h4, h5, h6, pre, div{
  display: block;
}
i{
  font-style: italic;
}
b{
  font-weight: bold;
}
a{
  color: #abcdef;
}
"""

TEI_WRAPPER = '''<?xml version="1.0" encoding="UTF-8"?>
<?xml-stylesheet type="text/xsl" href="../xsl/teibp.xsl"?>
<TEI xmlns="http://www.tei-c.org/ns/1.0">
  <teiHeader>
    <fileDesc>
      <titleStmt>
        <title>[TITLE]</title>
        <author>[AUTHOR]</author>
      </titleStmt>
      <publicationStmt>
        <p>Obra disponível em formato TEI</p>
      </publicationStmt>
        <respStmt>
          <resp>Encoded by</resp>
          <name>BDLP HTML2TEI translator</name>
        </respStmt>
    </fileDesc>
  </teiHeader>
'''