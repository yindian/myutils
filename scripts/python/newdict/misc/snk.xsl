<?xml version="1.0" encoding="UTF-8"?>

<xsl:stylesheet version="1.0"
xmlns:n="urn:xmlns:notknown"
xmlns:str="http://exslt.org/strings"
extension-element-prefixes="str"
xmlns:xsl="http://www.w3.org/1999/XSL/Transform">

<xsl:output method="html"/>
<xsl:strip-space elements="項目 解説部 大語義 語義"/>

<xsl:template match="/">
  <body>
    <xsl:apply-templates/>
  </body>
</xsl:template>

<xsl:template match="項目">
  <dl>
    <dt id="{@id}" noindex="1">
      <xsl:apply-templates select="見出部"/>
    </dt>
    <xsl:apply-templates select="見出部">
      <xsl:with-param name="key" select="'true'"/>
    </xsl:apply-templates>
    <dd>
      <xsl:apply-templates select="解説部"/>
    </dd>
  </dl>
  <xsl:apply-templates select="解説部/句項目">
    <xsl:with-param name="kukoumoku" select="'true'"/>
  </xsl:apply-templates>
  <xsl:apply-templates select="子項目"/>
</xsl:template>

<xsl:template match="項目/子項目">
  <dl>
    <dt id="{@id}" noindex="1">
      <xsl:apply-templates select="子見出部"/>
    </dt>
    <xsl:apply-templates select="子見出部">
      <xsl:with-param name="key" select="'true'"/>
    </xsl:apply-templates>
    <dd>
      <xsl:apply-templates select="子解説部"/>
    </dd>
  </dl>
</xsl:template>

<xsl:template match="項目/見出部/* | 項目/子項目/子見出部/*">
  <xsl:param name="key"/>
  <xsl:choose>
    <xsl:when test="string-length($key) = 0">
      <xsl:apply-templates/>
    </xsl:when>
    <xsl:otherwise>
      ！！！<xsl:value-of select="local-name()"/>
    </xsl:otherwise>
  </xsl:choose>
</xsl:template>

<xsl:template match="項目/見出部/見出仮名">
  <xsl:param name="key"/>
  <xsl:choose>
    <xsl:when test="string-length($key) = 0">
      <xsl:apply-templates/>
    </xsl:when>
    <xsl:otherwise>
      <key type="かな">
        <xsl:value-of select="."/>
      </key>
    </xsl:otherwise>
  </xsl:choose>
</xsl:template>

<xsl:template match="項目/子項目/子見出部/子見出仮名">
  <xsl:param name="key"/>
  <xsl:choose>
    <xsl:when test="string-length($key) = 0">
      <xsl:apply-templates/>
    </xsl:when>
    <xsl:otherwise>
    </xsl:otherwise>
  </xsl:choose>
</xsl:template>

<xsl:template match="項目/見出部/表記G | 項目/子項目/子見出部/表記G">
  <xsl:param name="key"/>
  <xsl:choose>
    <xsl:when test="string-length($key) = 0">
      <xsl:apply-templates/>
    </xsl:when>
    <xsl:otherwise>
      <xsl:call-template name="HYOKI"/>
    </xsl:otherwise>
  </xsl:choose>
</xsl:template>

<xsl:template match="//表記G/text()">
  <xsl:param name="dummy"/>
  <xsl:choose>
    <xsl:when test="string-length($dummy) = 0">
      <xsl:copy/>
    </xsl:when>
    <xsl:otherwise>
      <xsl:variable name="txt">
        <xsl:copy/>
      </xsl:variable>
      <xsl:choose>
        <xsl:when test="starts-with($txt, ':')">
          <xsl:value-of select="substring($txt, 2)"/>
        </xsl:when>
        <xsl:otherwise>
          <xsl:value-of select="$txt"/>
        </xsl:otherwise>
      </xsl:choose>
    </xsl:otherwise>
  </xsl:choose>
</xsl:template>

<xsl:template name="HYOKI">
  <xsl:variable name="hyoki">
    <xsl:apply-templates>
      <xsl:with-param name="dummy" select="'true'"/>
    </xsl:apply-templates>
  </xsl:variable>
  <xsl:choose>
    <xsl:when test="starts-with($hyoki, '［') and contains($hyoki, '］')">
      <xsl:for-each select="str:tokenize(substring-before(substring($hyoki, 2), '］'), '・')">
        <key type="表記">
          <xsl:value-of select="."/>
        </key>
      </xsl:for-each>
    </xsl:when>
    <xsl:when test="starts-with($hyoki, '〔←') and contains($hyoki, '〕')">
      <key type="表記">
        <xsl:value-of select="substring-before(substring($hyoki, 3), '〕')"/>
      </key>
    </xsl:when>
    <xsl:when test="starts-with($hyoki, '〔') and contains($hyoki, '〕')">
      <key type="表記">
        <xsl:value-of select="substring-before(substring($hyoki, 2), '〕')"/>
      </key>
    </xsl:when>
    <xsl:when test="substring($hyoki, string-length($hyoki)) = ''">
      <key type="表記">
        <xsl:value-of select="substring($hyoki, 1, string-length($hyoki) - 1)"/>
      </key>
    </xsl:when>
    <xsl:otherwise>
      ！！！<xsl:value-of select="$hyoki"/>
    </xsl:otherwise>
  </xsl:choose>
</xsl:template>

<xsl:template match="項目/見出部/品詞G | 項目/子項目/子見出部/品詞G">
  <xsl:param name="key"/>
  <xsl:choose>
    <xsl:when test="string-length($key) = 0">
      <i><xsl:apply-templates/></i>
    </xsl:when>
    <xsl:otherwise>
    </xsl:otherwise>
  </xsl:choose>
</xsl:template>

<xsl:template match="項目/見出部/歴史仮名 | 項目/子項目/子見出部/歴史仮名">
  <xsl:param name="key"/>
  <xsl:choose>
    <xsl:when test="string-length($key) = 0">
      <xsl:apply-templates/>
    </xsl:when>
    <xsl:otherwise>
    </xsl:otherwise>
  </xsl:choose>
</xsl:template>

<xsl:template match="項目/見出部/原綴 | 項目/子項目/子見出部/原綴">
  <xsl:param name="key"/>
  <xsl:choose>
    <xsl:when test="string-length($key) = 0">
      <xsl:apply-templates/>
    </xsl:when>
    <xsl:otherwise>
      <xsl:call-template name="HYOKI"/>
    </xsl:otherwise>
  </xsl:choose>
</xsl:template>

<xsl:template match="項目/見出部/語源 | 項目/子項目/子見出部/語源">
  <xsl:param name="key"/>
  <xsl:choose>
    <xsl:when test="string-length($key) = 0">
    </xsl:when>
    <xsl:otherwise>
      <p><xsl:apply-templates/></p>
    </xsl:otherwise>
  </xsl:choose>
</xsl:template>

<xsl:template match="項目/見出部/注解 | 項目/子項目/子見出部/注解">
  <xsl:param name="key"/>
  <xsl:choose>
    <xsl:when test="string-length($key) = 0">
    </xsl:when>
    <xsl:otherwise>
      <p><xsl:apply-templates/></p>
    </xsl:otherwise>
  </xsl:choose>
</xsl:template>

<xsl:template match="項目/解説部/* | 項目/子項目/子解説部/*">
  <xsl:param name="key"/>
  <xsl:choose>
    <xsl:when test="string-length($key) = 0">
      <xsl:apply-templates/>
    </xsl:when>
    <xsl:otherwise>
      ！！！<xsl:value-of select="local-name()"/>
    </xsl:otherwise>
  </xsl:choose>
</xsl:template>

<xsl:template match="//句項目">
  <xsl:param name="kukoumoku"/>
  <xsl:choose>
    <xsl:when test="string-length($kukoumoku) = 0">
    </xsl:when>
    <xsl:otherwise>
      <dl>
        <dt id="{@id}">
          <xsl:apply-templates select="句見出部"/>
        </dt>
        <xsl:apply-templates select="句見出部">
          <xsl:with-param name="key" select="'true'"/>
        </xsl:apply-templates>
        <dd>
          <xsl:apply-templates select="句解説部"/>
        </dd>
      </dl>
    </xsl:otherwise>
  </xsl:choose>
</xsl:template>

<xsl:template match="//句見出部">
  <xsl:param name="key"/>
  <xsl:choose>
    <xsl:when test="string-length($key) = 0">
      <xsl:apply-templates/>
    </xsl:when>
    <xsl:otherwise>
      <xsl:call-template name="HYOKI"/>
    </xsl:otherwise>
  </xsl:choose>
</xsl:template>

<xsl:template match="//句見出部/*">
  ！！！<xsl:value-of select="local-name()"/>
</xsl:template>

<xsl:template match="//句解説部/*">
  ！！！<xsl:value-of select="local-name()"/>
</xsl:template>

<xsl:template match="//大語義">
  <p><xsl:if test="@num">
      <xsl:value-of select="@num"/>
  </xsl:if><indent val="1"/><xsl:apply-templates/><indent val="0"/></p>
</xsl:template>

<xsl:template match="//大語義/*">
  ！！！<xsl:value-of select="local-name()"/>
</xsl:template>

<xsl:template match="//大語義/専門G">
  <b><xsl:apply-templates/></b>
</xsl:template>

<xsl:template match="//大語義/注記">
  <p><i><xsl:apply-templates/></i></p>
</xsl:template>

<xsl:template match="//大語義/語義">
  <p><xsl:if test="@num">
      <xsl:value-of select="@num"/>
  </xsl:if><indent val="2"/><xsl:apply-templates/><indent val="1"/></p>
</xsl:template>

<xsl:template match="//大語義/見出部要素">
  <i><xsl:apply-templates/></i>
</xsl:template>

<xsl:template match="//大語義/使用域G">
  <b><xsl:apply-templates/></b>
</xsl:template>

<xsl:template match="//大語義/語義/*">
  ！！！<xsl:value-of select="local-name()"/>
</xsl:template>

<xsl:template match="//大語義/語義/見出部要素">
  <i><xsl:apply-templates/></i>
</xsl:template>

<xsl:template match="//大語義/語義/副義">
  <p><xsl:if test="@num">
      <xsl:value-of select="@num"/>
  </xsl:if><indent val="3"/><xsl:apply-templates/><indent val="2"/></p>
</xsl:template>

<xsl:template match="//大語義/語釈">
  <xsl:apply-templates/>
</xsl:template>

<xsl:template match="//自動詞形G">
  <xsl:apply-templates/>
</xsl:template>

<xsl:template match="//他動詞形G">
  <xsl:apply-templates/>
</xsl:template>

<xsl:template match="//名詞形G">
  <xsl:apply-templates/>
</xsl:template>

<xsl:template match="//可能形G">
  <xsl:apply-templates/>
</xsl:template>

<xsl:template match="//対義語G">
  <xsl:apply-templates/>
</xsl:template>

<xsl:template match="//派生語G">
  <xsl:apply-templates/>
</xsl:template>

<xsl:template match="//動詞形G">
  <xsl:apply-templates/>
</xsl:template>

<xsl:template match="//共通">
  <xsl:apply-templates/>
</xsl:template>

<xsl:template match="//表記情報">
  <xsl:apply-templates/>
</xsl:template>

<xsl:template match="//参照G">
  <xsl:apply-templates/>
</xsl:template>

<xsl:template match="//参照G/*">
  ！！！<xsl:value-of select="local-name()"/>
</xsl:template>

<xsl:template match="//ref">
  <a href="#{@idref}"><xsl:apply-templates/></a>
</xsl:template>

<xsl:template match="//n:*">
  ！！！<xsl:value-of select="local-name()"/>
</xsl:template>

<xsl:template match="//n:sup">
  <xsl:param name="dummy"/>
  <xsl:if test="string-length($dummy) = 0">
    <sup><xsl:apply-templates/></sup>
  </xsl:if>
</xsl:template>

<xsl:template match="//n:sm">
  <xsl:param name="dummy"/>
  <xsl:if test="string-length($dummy) = 0">
    <sub><xsl:apply-templates/></sub>
  </xsl:if>
</xsl:template>

<xsl:template match="//n:sub">
  <xsl:param name="dummy"/>
  <xsl:choose>
    <xsl:when test="string-length($dummy) = 0">
      <sub><xsl:apply-templates/></sub>
    </xsl:when>
    <xsl:otherwise>
      <xsl:apply-templates/>
    </xsl:otherwise>
  </xsl:choose>
</xsl:template>

<xsl:template match="//n:i">
  <xsl:param name="dummy"/>
  <xsl:choose>
    <xsl:when test="string-length($dummy) = 0">
      <i><xsl:apply-templates/></i>
    </xsl:when>
    <xsl:otherwise>
      <xsl:apply-templates/>
    </xsl:otherwise>
  </xsl:choose>
</xsl:template>

<xsl:template match="//n:b">
  <xsl:param name="dummy"/>
  <xsl:choose>
    <xsl:when test="string-length($dummy) = 0">
      <b><xsl:apply-templates/></b>
    </xsl:when>
    <xsl:otherwise>
      <xsl:apply-templates/>
    </xsl:otherwise>
  </xsl:choose>
</xsl:template>

<xsl:template match="//n:r">
  <xsl:param name="dummy"/>
  <xsl:if test="string-length($dummy) = 0">
    <xsl:apply-templates/>
  </xsl:if>
</xsl:template>

<xsl:template match="//n:j">
  <xsl:apply-templates/>
</xsl:template>

<xsl:template match="//n:k">
  <xsl:apply-templates/>
</xsl:template>

<xsl:template match="//n:g">
  <xsl:param name="dummy"/>
  <xsl:choose>
    <xsl:when test="string-length($dummy) = 0">
      <strong><xsl:apply-templates/></strong>
    </xsl:when>
    <xsl:otherwise>
      <xsl:apply-templates/>
    </xsl:otherwise>
  </xsl:choose>
</xsl:template>

</xsl:stylesheet> 
