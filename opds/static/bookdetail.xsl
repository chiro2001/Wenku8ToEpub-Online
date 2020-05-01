﻿<?xml version="1.0" encoding="UTF-8"?>
<xsl:stylesheet version="1.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform">


    <xsl:template match="/">
        <html>
            <head>
                <title>
                    <xsl:value-of select="feed/title"/>
                </title>
                <meta charset="UTF-8"/>
                <meta name="viewport" content="width=device-width, initial-scale=1.0"/>
                <link rel="stylesheet" href="/static/bootstrap.min.css"/>
                <link rel="stylesheet" href="/static/bootstrap-responsive.min.css"/>
                <style type="text/css">
                    body { font-family: "Trebuchet MS", verdana, sans-serif; font-size: 76%;}

                    img { border: 0; }

                    .logo { float: left; margin-bottom: 20px;}

                    .accred { float: left; color: #444; }
                    .accred strong { display: block; margin-bottom: 5px; }

                    div.intro { clear: both; }

                    h2 { color: #0B0F4C; }

                    .pubdate{
                    font-size:10px;
                    font-style:italic;
                    }

                    .description{

                    }

                    .header {font-size:16px; margin: 0 0 0 0; color: #4F7FC9; }
                    .header a {font-size:20px; color: #4F7FC9 ; }
                    .header a:hover { font-size:23px;color: #4F7FC9; }
                    .header a.visited { font-size:16px;color: #4F7FC9; }

                </style>
            </head>

            <body style="font-family:helvetica,arial;">

                <div class="container">
                    <div class="row">
                        <div class="span1">
                            <div class="accred">
                                <a href="/">
                                    <img src="/static/logo.png" align="left"
                                         alt="opds logo" border="0" width="50px"/>
                                </a>
                            </div>
                        </div>
                        <div class="span4">
                            <h1>
                                <xsl:value-of select="/feed/title"/>
                            </h1>
                        </div>
                    </div>
                    <div class="description row">
                        <p class="span8">
                            <xsl:value-of select="/feed/description"/>
                        </p>

                    </div>
                    <div class="container header" style="margin-bottom:10px">
                        <a href="javascript:history.go(-1);">
                            <strong>&lt; 返回</strong>
                        </a>
                    </div>
                    <div class="container">
                        <xsl:for-each select="/feed/entry">
                            <div class="item row-fluid">
                                <div class="span2">
                                    <xsl:for-each select="link">
                                        <xsl:if test="contains(.,'jpg')">
                                            <img src="{.}"></img>
                                        </xsl:if>
                                    </xsl:for-each>
                                </div>
                                <div class="span10">
                                    <h3 class="header">
                                        <a
                                                href="{id}">
                                            <xsl:value-of select="title"></xsl:value-of>
                                        </a>
                                    </h3>
                                    <p class="pubdate">
                                        <xsl:value-of select="updated"/>
                                    </p>
                                    <span style="font-size:13pt" id="content">
                                        <xsl:value-of select="content" disable-output-escaping="yes"/>
                                    </span>
                                    <div>
                                        下载链接：
                                        <ul>
                                            <xsl:for-each select="link">
                                                <xsl:if test="contains(.,'pdf')">
                                                    <li>
                                                        <a href="{.}">
                                                            PDF
                                                        </a>
                                                    </li>
                                                </xsl:if>
                                                <xsl:if test="contains(.,'mobi')">
                                                    <li>
                                                        <a href="{.}">
                                                            MOBI
                                                        </a>
                                                    </li>
                                                </xsl:if>
                                                <xsl:if test="contains(.,'epub')">
                                                    <li>
                                                        <a href="{.}">
                                                            EPUB
                                                        </a>
                                                    </li>
                                                </xsl:if>
                                                <xsl:if test="contains(.,'opf')">

                                                    <span style="visibility:hidden;position:absolute">
                                                        <input type="text" id="opflink" value="{.}">

                                                        </input>
                                                    </span>
                                                </xsl:if>
                                            </xsl:for-each>
                                        </ul>
                                    </div>
                                </div>
                            </div>
                            <hr/>
                        </xsl:for-each>
                    </div>
                </div>
            </body>
            <script src="/static/jquery.min.js"></script>
            <script type="text/javascript">

                $.ajax({
                url: $("#opflink").val(),
                dataType: 'xml',
                success: function(data){
                var tt=$(data).find("package").find("metadata").find("description").text();

                $("#content").html(tt);
                }
                });
            </script>
        </html>
    </xsl:template>

    <xsl:output method="html"
                encoding="UTF-8"
                indent="no"/>


</xsl:stylesheet>