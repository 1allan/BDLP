<?xml version="1.0" encoding="UTF-8"?>
<xsl:stylesheet version="1.0"
                xmlns:xsl="http://www.w3.org/1999/XSL/Transform" 
                xmlns:eg="http://www.tei-c.org/ns/Examples"
                xmlns:tei="http://www.tei-c.org/ns/1.0" 
                xmlns:xd="http://www.oxygenxml.com/ns/doc/xsl"
                xmlns:exsl="http://exslt.org/common"
                xmlns:msxsl="urn:schemas-microsoft-com:xslt"
                xmlns:fn="http://www.w3.org/2005/xpath-functions"
                extension-element-prefixes="exsl msxsl"
                xmlns="http://www.w3.org/1999/xhtml" 
                xmlns:html="http://www.w3.org/1999/xhtml" 
                exclude-result-prefixes="xsl tei xd eg fn #default">

    <xd:doc scope="stylesheet">
        <xd:desc>
            <xd:p>
                <xd:b>Created on:</xd:b> Nov 17, 2011</xd:p>
            <xd:p>
                <xd:b>Author:</xd:b> John A. Walsh</xd:p>
            <xd:p>TEI Boilerplate stylesheet: Copies TEI document, with a very few modifications
                into an html shell, which provides access to javascript and other features from the
                html/browser environment.</xd:p>
        </xd:desc>
    </xd:doc>
    <xsl:include href="xml-to-string.xsl"/>

    <xsl:output encoding="UTF-8" method="xml" omit-xml-declaration="yes"/>
	
    <xsl:param name="teibpHome" select="'http://dcl.slis.indiana.edu/teibp/'"/>
    <xsl:param name="inlineCSS" select="false()"/>
    <xsl:param name="includeToolbox" select="false()"/>
    <xsl:param name="displayPageBreaks" select="true()"/>
	
    <!-- special characters -->
    <xsl:param name="quot">
        <text>"</text>
    </xsl:param>
    <xsl:param name="apos">
        <text>'</text>
    </xsl:param>
	
    <!-- interface text -->
    <xsl:param name="pbNote">
        <text>page: </text>
    </xsl:param>
    <xsl:param name="altTextPbFacs">
        <text>view page image(s)</text>
    </xsl:param>
    
    <xsl:param name="filePrefix" select="'..'"/>
    <xsl:param name="teibpcss" select="concat($filePrefix,'/css/teibp.css')"/>
    <xsl:param name="customcss" select="concat($filePrefix,'/css/custom.css')"/>
    <xsl:param name="teibpJS" select="concat($filePrefix,'/js/teibp.js')"/>
    <xsl:param name="downloadJS" select="concat($filePrefix,'/js/download.js')"/>
    <xsl:param name="theme.default" select="concat($filePrefix,'/css/teibp.css')"/>
    <xsl:param name="theme.sleepytime" select="concat($filePrefix,'/css/sleepy.css')"/>
    <xsl:param name="theme.terminal" select="concat($filePrefix,'/css/terminal.css')"/>
    <xsl:param name="mediaqueries" select="concat($filePrefix,'/css/mediaqueries.css')"/>
    <xsl:param name="mainJS" select="concat($filePrefix,'/js/main.js')"/>
        
    <xd:doc xmlns:xd="http://www.oxygenxml.com/ns/doc/xsl">
        <xd:desc>
            <xd:p>Match document root and create and html5 wrapper for the TEI document, which is
                copied, with some modification, into the HTML document.</xd:p>
        </xd:desc>
    </xd:doc>
    <xsl:key name="ids" match="//*" use="@xml:id"/>

    <xsl:template match="/" name="htmlShell" priority="99">
        <html>
            <xsl:call-template name="htmlHead"/>
            <body class="anti-fouc">
                <header>
                    <a class="logo-bdlp" href="https://www.literaturabrasileira.ufsc.br/?locale=pt_BR">BLPL</a>
                    <nav>
                        <div id="download-button" class="tooltip bottom" data-content="Baixar o texto">
                            <a id="download" onclick="return downloadHTML();" download="">
                                <img src="../images/download.svg" alt="Baixar o texto"/>
                            </a>
                        </div>
                        <div id="theme-switch" class="tooltip bottom" data-content="Alterar contraste">
                            <img src="../images/theme-switch.svg" alt="Mudar tema"/>
                        </div>
                        <div id="index-button" class="menu-button open tooltip bottom" data-content="Sumário">
                            <span class="line top"></span>
                            <span class="line middle"></span>
                            <span class="line bottom"></span>
                        </div>
                    </nav>
                    <xsl:call-template name="indexMenu"/>
                </header>
                <xsl:if test="$includeToolbox = true()">
                    <xsl:call-template name="teibpToolbox"/>
                </xsl:if>
                <div id="tei-wrapper">
                    <xsl:apply-templates/>
                </div>
                <xsl:copy-of select="$htmlFooter"/>
                <script type="text/javascript" src="{$teibpJS}"></script>
                <script type="text/javascript" src="{$mainJS}"></script>
                <script type="text/javascript" src="{$downloadJS}"></script>
                <div id="device-alert">
                    <span>Para uma melhor legibilidade, recomendamos mudar a orientação do dispositivo!</span>
                </div>
            </body>
        </html>
    </xsl:template>

    <xd:doc>
        <xd:desc>
            <xd:p>Basic copy template, copies all attribute nodes from source XML tree to output
                document.</xd:p>
        </xd:desc>
    </xd:doc>
    <xsl:template match="@*">
        <xsl:copy/>
    </xsl:template>

    <xd:doc>
        <xd:desc>
            <xd:p>Template for elements, which handles style and adds an @xml:id to every element.
                Existing @xml:id attributes are retained unchanged.</xd:p>
        </xd:desc>
    </xd:doc>
    <xsl:template match="*" name="teibp-default">
        <xsl:element name="{local-name()}">
            <xsl:apply-templates select="@*"/>
            <xsl:call-template name="addID"/>
            <xsl:call-template name="rendition"/>
            <xsl:apply-templates select="node()"/>
        </xsl:element>
    </xsl:template>
	
    <xd:doc>
        <xd:desc>
            <xd:p>A hack because JavaScript was doing weird things with &lt;title>, probably due to confusion with HTML title. There is no TEI namespace in the TEI Boilerplate output because JavaScript, or at least JQuery, cannot manipulate the TEI elements/attributes if they are in the TEI namespace, so the TEI namespace is stripped from the output. As far as I know, &lt;title> elsewhere does not cause any problems, but we may need to extend this to other occurrences of &lt;title> outside the Header.</xd:p>
        </xd:desc>
    </xd:doc>
    <xsl:template match="tei:teiHeader//tei:title">
        <tei-title>
            <xsl:call-template name="addID"/>
            <xsl:apply-templates select="@*|node()"/>
        </tei-title>
    </xsl:template>

    <xd:doc xmlns:xd="http://www.oxygenxml.com/ns/doc/xsl">
        <xd:desc>
            <xd:p>Template to omit processing instructions from output.</xd:p>
        </xd:desc>
    </xd:doc>
    <xsl:template match="processing-instruction()" priority="10"/>

    <xd:doc xmlns:xd="http://www.oxygenxml.com/ns/doc/xsl">
        <xd:desc>
            <xd:p>Template moves value of @rend into an html @style attribute. Stylesheet assumes
                CSS is used in @rend to describe renditions, i.e., styles.</xd:p>
        </xd:desc>
    </xd:doc>
    <xsl:template match="@rend">
        <xsl:choose>
            <xsl:when test="$inlineCSS = true()">
                <xsl:attribute name="style">
                    <xsl:value-of select="."/>
                </xsl:attribute>
            </xsl:when>
            <xsl:otherwise>
                <xsl:copy>
                    <xsl:apply-templates select="@*|node()"/>
                </xsl:copy>
            </xsl:otherwise>
        </xsl:choose>
    </xsl:template>
	
    <xsl:template name="rendition">
        <xsl:if test="@rendition">
            <xsl:attribute name="rendition">
                <xsl:value-of select="@rendition"/>
            </xsl:attribute>
        </xsl:if>
    </xsl:template>
	
    <xsl:template match="@xml:id">
        <xsl:attribute name="id">
            <xsl:value-of select="."/>
        </xsl:attribute>
    </xsl:template>

    <xd:doc>
        <xd:desc>
            <xd:p>Transforms TEI ref element to html a (link) element.</xd:p>
        </xd:desc>
    </xd:doc>
    <xsl:template match="tei:ref[@target]" priority="99">
        <a href="{@target}">
            <xsl:apply-templates select="@*"/>
            <xsl:call-template name="rendition"/>
            <xsl:apply-templates select="node()"/>
        </a>
    </xsl:template>

    <xd:doc>
        <xd:desc>
            <xd:p>Transforms TEI ptr element to html a (link) element.</xd:p>
        </xd:desc>
    </xd:doc>
    <xsl:template match="tei:ptr[@target]" priority="99">
        <a href="{@target}">
            <xsl:apply-templates select="@*"/>
            <xsl:call-template name="rendition"/>
            <xsl:value-of select="normalize-space(@target)"/>
        </a>
    </xsl:template>

    <!-- need something else for images with captions -->
    <xd:doc>
        <xd:desc>
            <xd:p>Transforms TEI figure element to html img element.</xd:p>
        </xd:desc>
    </xd:doc>
    <xsl:template match="tei:figure[tei:graphic[@url]]" priority="99">
        <xsl:copy>
            <xsl:apply-templates select="@*"/>
            <xsl:call-template name="addID"/>
            <figure>
                <img alt="{normalize-space(tei:figDesc)}" src="{tei:graphic/@url}"/>
                <xsl:apply-templates select="*[ not( self::tei:graphic | self::tei:figDesc ) ]"/>
            </figure>
        </xsl:copy>
    </xsl:template>
	
    <xsl:template name="addID">
        <xsl:if test="not(ancestor::eg:egXML)">
            <xsl:attribute name="id">
                <xsl:choose>
                    <xsl:when test="@xml:id">
                        <xsl:value-of select="@xml:id"/>
                    </xsl:when>
                    <xsl:otherwise>
                        <xsl:call-template name="generate-unique-id">
                            <xsl:with-param name="root" select="generate-id()"/>
                        </xsl:call-template>
                    </xsl:otherwise>
                </xsl:choose>
            </xsl:attribute>
        </xsl:if>
    </xsl:template>

    <xd:doc xmlns:xd="http://www.oxygenxml.com/ns/doc/xsl">
        <xd:desc>
            <xd:p>The generate-id() function does not guarantee the generated id will not conflict
                with existing ids in the document. This template checks for conflicts and appends a
                number (hexedecimal 'f') to the id. The template is recursive and continues until no
                conflict is found</xd:p>
        </xd:desc>
        <xd:param name="root">The root, or base, id used to check for conflicts</xd:param>
        <xd:param name="suffix">The suffix added to the root id if a conflict is
            detected.</xd:param>
    </xd:doc>
    <xsl:template name="generate-unique-id">
        <xsl:param name="root"/>
        <xsl:param name="suffix"/>
        <xsl:variable name="id" select="concat($root,$suffix)"/>
        <xsl:choose>
            <xsl:when test="key('ids',$id)">
                <xsl:call-template name="generate-unique-id">
                    <xsl:with-param name="root" select="$root"/>
                    <xsl:with-param name="suffix" select="concat($suffix,'f')"/>
                </xsl:call-template>
            </xsl:when>
            <xsl:otherwise>
                <xsl:value-of select="$id"/>
            </xsl:otherwise>
        </xsl:choose>
    </xsl:template>

    <xd:doc xmlns:xd="http://www.oxygenxml.com/ns/doc/xsl">
        <xd:desc>
            <xd:p>Template for adding /html/head content.</xd:p>
        </xd:desc>
    </xd:doc>
    <xsl:template name="htmlHead">
        <head type="document-head">
            <meta charset="UTF-8"/>
            <meta name="viewport" content="width=device-width, initial-scale=1"/>

            <link rel="stylesheet" type="text/css" href="https://fonts.googleapis.com/css?family=Oxygen:300,400"/>
            <link rel="stylesheet" type="text/css" href="https://fonts.googleapis.com/css?family=Source+Sans+Pro:400,600,700"/>
            <link rel="stylesheet" type="text/css" href="https://fonts.googleapis.com/css?family=Roboto"/>
            <link rel="stylesheet" type="text/css" href="http://fonts.googleapis.com/css?family=Arvo:700,700italic|Gentium+Book+Basic:400,400italic,700,700italic"/>
            <link id="maincss" rel="stylesheet" type="text/css" href="{$teibpcss}"/>
            <link id="customcss" rel="stylesheet" type="text/css" href="{$customcss}"/>
            <link id="mediaqueries" rel="stylesheet" type="text/css" href="{$mediaqueries}"/>

            <xsl:call-template name="tagUsage2style"/>
            <xsl:call-template name="rendition2style"/>
            <title><!-- don't leave empty. --></title>
        </head>
    </xsl:template>

    <xsl:template name="rendition2style">
        <style type="text/css">
            <xsl:apply-templates select="//tei:rendition" mode="rendition2style"/>
        </style>
    </xsl:template>
  
    <!-- tag usage support -->
  
    <xsl:template name="tagUsage2style">
        <style type="text/css" id="tagusage-css">
            <xsl:for-each select="//tei:namespace[@name ='http://www.tei-c.org/ns/1.0']/tei:tagUsage">
                <xsl:value-of select="concat('&#x000a;',@gi,' { ')"/>
                <xsl:call-template name="tokenize">
                    <xsl:with-param name="string" select="@render" />
                </xsl:call-template>
                <xsl:value-of select="'}&#x000a;'"/>
            </xsl:for-each>
        </style>
    </xsl:template>
  
    <xsl:template name="tokenize">
        <xsl:param name="string" />
        <xsl:param name="delimiter" select="' '" />
        <xsl:choose>
            <xsl:when test="$delimiter and contains($string, $delimiter)">
                <xsl:call-template name="grab-css">
                    <xsl:with-param name="rendition-id" select="substring-after(substring-before($string, $delimiter),'#')" />
                </xsl:call-template>
                <xsl:text> </xsl:text>
                <xsl:call-template name="tokenize">
                    <xsl:with-param name="string" 
                                    select="substring-after($string, $delimiter)" />
                    <xsl:with-param name="delimiter" select="$delimiter" /> 
                </xsl:call-template>
            </xsl:when>
            <xsl:otherwise>
                <xsl:call-template name="grab-css">
                    <xsl:with-param name="rendition-id" select="substring-after($string,'#')"/>
                </xsl:call-template>
            </xsl:otherwise>
        </xsl:choose>
    </xsl:template>
  
    <xsl:template name="grab-css">
        <xsl:param name="rendition-id"/>
        <xsl:value-of select="normalize-space(key('ids',$rendition-id)/text())"/>
    </xsl:template>
	
    <xsl:template match="tei:rendition[@xml:id and @scheme = 'css']" mode="rendition2style">
        <xsl:value-of select="concat('[rendition~=&quot;#',@xml:id,'&quot;]')"/>
        <xsl:if test="@scope">
            <xsl:value-of select="concat(':',@scope)"/>
        </xsl:if>
        <xsl:value-of select="concat('{ ',normalize-space(.),'}&#x000A;')"/>
    </xsl:template>
	
    <xsl:template match="tei:rendition[not(@xml:id) and @scheme = 'css' and @corresp]" mode="rendition2style">
        <xsl:value-of select="concat('[rendition~=&quot;#',substring-after(@corresp,'#'),'&quot;]')"/>
        <xsl:if test="@scope">
            <xsl:value-of select="concat(':',@scope)"/>
        </xsl:if>
        <xsl:value-of select="concat('{ ',normalize-space(.),'}&#x000A;')"/>
    </xsl:template>
    <xd:doc xmlns:xd="http://www.oxygenxml.com/ns/doc/xsl">
        <xd:desc>
            <xd:p>Template for adding footer to html document.</xd:p>
        </xd:desc>
    </xd:doc>
    <xsl:variable name="htmlFooter">
        <footer> 
            <span>Powered by <a href="{$teibpHome}">TEI Boilerplate</a>.</span>
            <span>TEI Boilerplate is licensed under a <a href="http://creativecommons.org/licenses/by/3.0/">Creative Commons Attribution 3.0 Unported License</a>.</span>
            <a href="http://creativecommons.org/licenses/by/3.0/">
                <img alt="Creative Commons License" style="border-width:0;" src="https://licensebuttons.net/l/by/3.0/80x15.png"/>
            </a>
        </footer>
    </xsl:variable>

    <xsl:template name="teibpToolbox">
        <div id="teibpToolbox">
            <h1>Toolbox</h1>
            <label for="pbToggle">Hide page breaks</label>
            <input type="checkbox" id="pbToggle" /> 
            <div>
                <h3>Themes:</h3>
                <select id="themeBox" onchange="switchThemes(this);">
                    <option value="{$theme.default}" >Default</option>
                    <option value="{$theme.sleepytime}">Sleepy Time</option>
                    <option value="{$theme.terminal}">Terminal</option>
                </select>			
            </div>
        </div>
    </xsl:template>	
    <xsl:template name="pb-handler">
        <xsl:param name="n"/>
        <xsl:param name="facs"/>
        <xsl:param name="id"/>
        <!-- dealing with pointers instead of full URLs in @facs -->
        <xsl:variable name="vFacs">
            <xsl:choose>
                <xsl:when test="starts-with($facs,'#')">
                    <xsl:variable name="vFacsID" select="substring-after($facs,'#')"/>
                    <xsl:variable name="vMimeType" select="'image/jpeg'"/>
                    <xsl:value-of select="ancestor::tei:TEI/tei:facsimile/tei:surface[@xml:id=$vFacsID]/tei:graphic[@mimeType=$vMimeType][1]/@url"/>
                </xsl:when>
                <xsl:otherwise>
                    <xsl:value-of select="$facs"/>
                </xsl:otherwise>
            </xsl:choose>
        </xsl:variable>
		
        <span class="-teibp-pageNum">
            <!-- <xsl:call-template name="atts"/> -->
            <span class="-teibp-pbNote">
                <xsl:value-of select="$pbNote"/>
            </span>
            <xsl:value-of select="@n"/>
            <xsl:text> </xsl:text>
        </span>
        <span class="-teibp-pbFacs">
            <a class="gallery-facs" rel="prettyPhoto[gallery1]">
                <xsl:attribute name="onclick">
                    <xsl:value-of select="concat('showFacs(',$apos,$n,$apos,',',$apos,$vFacs,$apos,',',$apos,$id,$apos,')')"/>
                </xsl:attribute>
                <img  alt="{$altTextPbFacs}" class="-teibp-thumbnail">
                    <xsl:attribute name="src">
                        <xsl:value-of select="$vFacs"/>
                    </xsl:attribute>
                </img>
            </a>
        </span>

    </xsl:template>
	
    <xsl:template match="tei:pb[@facs]">
        <xsl:param name="pn">
            <xsl:number count="//tei:pb" level="any"/>    
        </xsl:param>
        <xsl:choose>
            <xsl:when test="$displayPageBreaks = true()">
                <!-- add @lang="en" to ensure correct ltr rendering -->
                <span class="-teibp-pb" lang="en">
                    <xsl:call-template name="addID"/>
                    <xsl:call-template name="pb-handler">
                        <xsl:with-param name="n" select="@n"/>
                        <xsl:with-param name="facs" select="@facs"/>
                        <xsl:with-param name="id">
                            <xsl:choose>
                                <xsl:when test="@xml:id">
                                    <xsl:value-of select="@xml:id"/>
                                </xsl:when>
                                <xsl:otherwise>
                                    <xsl:value-of select="generate-id()"/>
                                </xsl:otherwise>
                            </xsl:choose>
                        </xsl:with-param>
                    </xsl:call-template>
                </span>
            </xsl:when>
            <xsl:otherwise>
                <xsl:copy>
                    <xsl:apply-templates select="@*|node()"/>
                </xsl:copy>
            </xsl:otherwise>
        </xsl:choose>
    </xsl:template>
	
    <xsl:template match="eg:egXML">
        <xsl:element name="{local-name()}">
            <xsl:apply-templates select="@*"/>
            <xsl:call-template name="addID"/>
            <xsl:call-template name="xml-to-string">
                <xsl:with-param name="node-set">
                    <xsl:copy-of select="node()"/>
                </xsl:with-param>
            </xsl:call-template>
        </xsl:element>
    </xsl:template>
	
    <xsl:template match="eg:egXML//comment()">
        <xsl:comment>
            <xsl:value-of select="."/>
        </xsl:comment>
    </xsl:template>
    
    <!-- support for rtl-languages such as Arabic -->
    <!-- template to add the HTML @lang attribute based on the containing element -->
    <xsl:template name="templHtmlAttrLang">
        <xsl:param name="pInput"/>
        <xsl:choose>
            <xsl:when test="$pInput/@xml:lang">
                <xsl:attribute name="lang">
                    <xsl:value-of select="$pInput/@xml:lang"/>
                </xsl:attribute>
            </xsl:when>
            <xsl:otherwise>
                <xsl:attribute name="lang">
                    <xsl:value-of select="ancestor::node()[@xml:lang!=''][1]/@xml:lang"/>
                </xsl:attribute>
            </xsl:otherwise>
        </xsl:choose>
    </xsl:template>
    
    <!-- add the @lang attribute to the <body> -->
    <xsl:template match="tei:body">
        <xsl:copy>
            <xsl:call-template name="templHtmlAttrLang">
                <xsl:with-param name="pInput" select="."/>
            </xsl:call-template>
            <xsl:apply-templates select="@* | node()"/>
        </xsl:copy>
    </xsl:template>

    <xsl:template match="//header/div[id='index-menu']" name="indexMenu">
        <div id="index-menu">
            <h1>Índice</h1>
            <xsl:for-each select="//tei:text//tei:head">
                <a href="#title{position() - 1}" data-depth="{count(ancestor::*) - 3}">
                    <xsl:value-of select="./text()"/>
                </a>
            </xsl:for-each>
        </div>
    </xsl:template>

    <!-- format theater speeches -->
    <xsl:template match="tei:l[@part='I']">
        <l type="dialogue">
            <row>
                <part>
                    <xsl:value-of select="."/>
                </part>
                <empty-cell/>
                <empty-cell/>
            </row>
            <xsl:choose>
                <xsl:when test="following-sibling::*[1]/@part='M'">
                    <row>
                        <empty-cell/>
                        <part>
                            <xsl:value-of select="following-sibling::*[1]"/>
                        </part>
                        <empty-cell/>
                    </row>
                    <row>
                        <empty-cell/>
                        <empty-cell/>
                        <part>
                            <xsl:value-of select="following-sibling::*[2]"/>
                        </part>
                    </row>
                </xsl:when>
                <xsl:otherwise>
                    <row>
                        <empty-cell/>
                        <empty-cell/>
                        <part>
                            <xsl:value-of select="following-sibling::*[1]"/>
                        </part>
                    </row>
                </xsl:otherwise>
            </xsl:choose>
			
        </l>
    </xsl:template>
    <xsl:template match="tei:l[@part='M']"/>
    <xsl:template match="tei:l[@part='F']"/>

	
    <!-- Format footnotes -->
    <xsl:template match="tei:body">
        <xsl:copy>
            <xsl:apply-templates select="@* | node()"/>
        </xsl:copy>
		&#160;
        <foot>
            <xsl:for-each select="//tei:text//tei:note[@place='foot']">
                <div>
                    <a class="note"  id="{concat('cit', count(preceding::tei:note))}" href="{concat('#cit', count(preceding::tei:note), 'return')}">
                        [<xsl:value-of select="count(preceding::tei:note)"/>] ↑
                    </a>
                    <div>
                        <xsl:value-of select="."/>
                        <xsl:if test="@resp">
                            <xsl:variable name="rsp" select="@resp"/>
			
                            (<xsl:value-of select="//tei:respStmt[tei:name[@xml:id=$rsp]]/tei:resp"/> - <xsl:value-of select="//tei:respStmt/tei:name[@xml:id=$rsp]"/>)
                        </xsl:if>
                    </div>
                </div>
            </xsl:for-each>
        </foot>
    </xsl:template>

    <xsl:template match="//tei:text//tei:note[@place='foot']">
        <xsl:variable name="pos" select="concat('#cit', count(preceding::tei:note))"/>
				
        <a class="note" id="{concat('cit', count(preceding::tei:note), 'return')}" href="{$pos}">
            [<xsl:value-of select="count(preceding::tei:note)"/>] <xsl:value-of select="position"/>
        </a>
    </xsl:template>
	
    <!-- Generate index -->
    <xsl:template match="//tei:TEI//tei:head">
        <xsl:copy>
            <xsl:attribute name="id">title<xsl:value-of select="count(preceding::tei:head)"/></xsl:attribute>
            <xsl:apply-templates select="@* | node()"/>
        </xsl:copy>
    </xsl:template>

    <xsl:template match="//tei:TEI//tei:text">
        <div id="index">
            <xsl:for-each select="//tei:text//tei:head">
                <a href="#title{position() - 1}" data-depth="{count(ancestor::*) - 3}">
                    <xsl:value-of select="./text()"/>
                </a>
            </xsl:for-each>
        </div>

        <xsl:copy>
            <xsl:apply-templates select="@* | node()"/>
        </xsl:copy>
    </xsl:template>

	<!-- Format sp tags for theater texts -->
	<xsl:template match="//tei:sp">
		<xsl:variable name="roleID" select="translate(./@who, '#', '')"/>
        <div class="uppercased">
            <xsl:value-of select="//tei:role[@xml:id=$roleID]"/>
        </div>
		<xsl:copy>
			<xsl:apply-templates select="@* | node()"/>
		</xsl:copy>
	</xsl:template>

</xsl:stylesheet>