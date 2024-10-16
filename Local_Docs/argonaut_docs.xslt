<?xml version="1.0" encoding="UTF-8"?>
<xsl:stylesheet version="1.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform">
<xsl:output method="html" indent="yes" encoding="UTF-8"/>

<xsl:template match="/">
  <html lang="en">
    <head>
      <meta charset="UTF-8"/>
      <meta name="viewport" content="width=device-width, initial-scale=1.0"/>
      <title>ArgøNaut: Advanced CLI Framework</title>
      <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0-beta3/css/all.min.css"/>
      <style>
        :root {
          --primary-color: #00ffff;
          --secondary-color: #ff00ff;
          --background-color: #111;
          --text-color: #f0f0f0;
          --link-color: #00ff00;
          --code-background: #1a1a1a;
          --header-font: 'Orbitron', sans-serif;
          --body-font: 'Roboto Mono', monospace;
        }
        @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700&amp;family=Roboto+Mono:wght@400;700&amp;display=swap');
        body {
          font-family: var(--body-font);
          line-height: 1.6;
          color: var(--text-color);
          background-color: var(--background-color);
          margin: 0;
          padding: 0;
          background-image: 
            radial-gradient(circle at 10% 20%, rgba(0, 255, 255, 0.05) 0%, transparent 20%),
            radial-gradient(circle at 90% 80%, rgba(255, 0, 255, 0.05) 0%, transparent 20%);
          background-attachment: fixed;
        }
        .container {
          max-width: 1200px;
          margin: 0 auto;
          padding: 20px;
        }
        .navbar {
          background-color: rgba(0, 0, 0, 0.8);
          backdrop-filter: blur(10px);
          padding: 15px 0;
          position: sticky;
          top: 0;
          z-index: 1000;
          box-shadow: 0 2px 10px rgba(0, 255, 255, 0.2);
        }
        .navbar-content {
          display: flex;
          justify-content: space-between;
          align-items: center;
          max-width: 1200px;
          margin: 0 auto;
          padding: 0 20px;
        }
        .navbar a {
          color: var(--primary-color);
          text-decoration: none;
          margin: 0 15px;
          font-weight: bold;
          text-transform: uppercase;
          letter-spacing: 1px;
          transition: color 0.3s ease;
        }
        .navbar a:hover {
          color: var(--secondary-color);
          text-shadow: 0 0 10px var(--secondary-color);
        }
        h1, h2, h3, h4, h5 {
          font-family: var(--header-font);
          color: var(--primary-color);
          text-transform: uppercase;
          letter-spacing: 2px;
          margin-top: 2em;
        }
        h1 { font-size: 3em; text-align: center; margin-bottom: 1em; text-shadow: 0 0 10px var(--primary-color); }
        h2 { font-size: 2.5em; border-bottom: 2px solid var(--primary-color); padding-bottom: 10px; }
        h3 { font-size: 2em; }
        h4 { font-size: 1.5em; }
        code {
          font-family: 'Roboto Mono', monospace;
          background-color: var(--code-background);
          color: var(--primary-color);
          padding: 2px 4px;
          border-radius: 4px;
        }
        pre {
          background-color: var(--code-background);
          padding: 20px;
          overflow-x: auto;
          border-radius: 8px;
          border: 1px solid var(--primary-color);
          box-shadow: 0 0 20px rgba(0, 255, 255, 0.1);
        }
        .section { 
          background-color: rgba(0, 0, 0, 0.6);
          border: 1px solid var(--primary-color);
          border-radius: 15px;
          padding: 30px;
          margin-bottom: 40px;
          box-shadow: 0 0 30px rgba(0, 255, 255, 0.1);
          transition: transform 0.3s ease, box-shadow 0.3s ease;
        }
        .section:hover {
          transform: translateY(-5px);
          box-shadow: 0 5px 30px rgba(0, 255, 255, 0.2);
        }
        .subsection { margin-left: 20px; }
        ul, ol { padding-left: 20px; }
        a { color: var(--link-color); text-decoration: none; transition: color 0.3s ease; }
        a:hover { color: var(--secondary-color); text-decoration: underline; }
        .method { 
          border-left: 4px solid var(--secondary-color);
          padding-left: 20px;
          margin-bottom: 30px;
          background-color: rgba(255, 0, 255, 0.05);
          border-radius: 0 15px 15px 0;
        }
        .parameter { font-style: italic; color: var(--secondary-color); }
        .example { 
          background-color: rgba(0, 0, 0, 0.8);
          border: 1px solid var(--secondary-color);
          border-radius: 15px;
          padding: 20px;
          margin: 20px 0;
        }
        ::-webkit-scrollbar { width: 12px; background-color: var(--background-color); }
        ::-webkit-scrollbar-thumb { 
          background-color: var(--primary-color);
          border-radius: 6px;
          border: 3px solid var(--background-color);
        }
        .icon { margin-right: 10px; }
        .glow {
          animation: glow 2s ease-in-out infinite alternate;
        }
        @keyframes glow {
          from { text-shadow: 0 0 5px var(--primary-color), 0 0 10px var(--primary-color); }
          to { text-shadow: 0 0 10px var(--primary-color), 0 0 20px var(--primary-color), 0 0 30px var(--primary-color); }
        }
        .feature-list {
          display: grid;
          grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
          gap: 20px;
          margin-top: 30px;
        }
        .feature-item {
          background-color: rgba(0, 255, 255, 0.05);
          border: 1px solid var(--primary-color);
          border-radius: 10px;
          padding: 20px;
          transition: transform 0.3s ease, box-shadow 0.3s ease;
        }
        .feature-item:hover {
          transform: translateY(-5px);
          box-shadow: 0 5px 15px rgba(0, 255, 255, 0.2);
        }
        .button {
          display: inline-block;
          padding: 10px 20px;
          background-color: var(--primary-color);
          color: var(--background-color);
          text-decoration: none;
          border-radius: 5px;
          transition: background-color 0.3s ease, transform 0.3s ease;
        }
        .button:hover {
          background-color: var(--secondary-color);
          transform: translateY(-2px);
        }
        @media (max-width: 768px) {
          .navbar-content {
            flex-direction: column;
            align-items: flex-start;
          }
          .navbar a {
            margin: 5px 0;
          }
        }
        .setup-steps, .contribution-list {
          padding-left: 20px;
          margin-top: 15px;
        }
        .setup-steps li, .contribution-list li {
          margin-bottom: 10px;
        }
        .substeps {
          margin-top: 10px;
          padding-left: 20px;
          list-style-type: circle;
        }
        .contribution-list li::before {
          content: "\f00c";
          font-family: "Font Awesome 5 Free";
          font-weight: 900;
          margin-right: 10px;
          color: var(--primary-color);
        }
      </style>
    </head>
    <body>
      <header>
        <nav class="navbar">
          <div class="navbar-content">
            <a href="#" class="glow">ArgøNaut</a>
            <div>
              <xsl:for-each select="argonaut-documentation/*[name() != 'introduction']">
                <a href="#{name()}">
                  <xsl:call-template name="get-icon">
                    <xsl:with-param name="section" select="name()"/>
                  </xsl:call-template>
                  <xsl:value-of select="translate(name(), '-', ' ')"/>
                </a>
              </xsl:for-each>
            </div>
          </div>
        </nav>
      </header>
      <div class="container">
        <main>
          <xsl:apply-templates select="argonaut-documentation/*"/>
        </main>
        <footer>
          <p>© 2024 ArgøNaut. Empowering the future of command-line interfaces.</p>
        </footer>
      </div>
    </body>
  </html>
</xsl:template>

<xsl:template name="get-icon">
  <xsl:param name="section"/>
  <xsl:choose>
    <xsl:when test="$section = 'installation'"><i class="fas fa-download icon"></i></xsl:when>
    <xsl:when test="$section = 'basic-usage'"><i class="fas fa-play icon"></i></xsl:when>
    <xsl:when test="$section = 'advanced-features'"><i class="fas fa-rocket icon"></i></xsl:when>
    <xsl:when test="$section = 'input-handling-and-validation'"><i class="fas fa-shield-alt icon"></i></xsl:when>
    <xsl:when test="$section = 'output-and-formatting'"><i class="fas fa-paint-brush icon"></i></xsl:when>
    <xsl:when test="$section = 'plugin-system'"><i class="fas fa-puzzle-piece icon"></i></xsl:when>
    <xsl:when test="$section = 'cross-platform-compatibility'"><i class="fas fa-globe icon"></i></xsl:when>
    <xsl:when test="$section = 'error-handling-and-logging'"><i class="fas fa-exclamation-triangle icon"></i></xsl:when>
    <xsl:when test="$section = 'best-practices-and-tips'"><i class="fas fa-lightbulb icon"></i></xsl:when>
    <xsl:when test="$section = 'api-reference'"><i class="fas fa-book icon"></i></xsl:when>
    <xsl:when test="$section = 'examples'"><i class="fas fa-code icon"></i></xsl:when>
    <xsl:when test="$section = 'troubleshooting'"><i class="fas fa-wrench icon"></i></xsl:when>
    <xsl:when test="$section = 'faq'"><i class="fas fa-question-circle icon"></i></xsl:when>
    <xsl:when test="$section = 'changelog'"><i class="fas fa-history icon"></i></xsl:when>
    <xsl:when test="$section = 'license'"><i class="fas fa-gavel icon"></i></xsl:when>
    <xsl:otherwise><i class="fas fa-file-alt icon"></i></xsl:otherwise>
  </xsl:choose>
</xsl:template>

<xsl:template match="introduction">
  <section id="introduction" class="section">
    <h1 class="glow"><xsl:value-of select="title"/></h1>
    <p><xsl:value-of select="description"/></p>
    <h3><i class="fas fa-star icon"></i>Key Features</h3>
    <div class="feature-list">
      <xsl:for-each select="key-features/feature">
        <div class="feature-item">
          <i class="fas fa-check icon"></i>
          <xsl:value-of select="."/>
        </div>
      </xsl:for-each>
    </div>
    <p class="text-center">
      <a href="#installation" class="button">Get Started</a>
    </p>
  </section>
</xsl:template>

<xsl:template match="installation">
  <section id="installation" class="section">
    <h2><i class="fas fa-download icon"></i>Installation</h2>
    <ol>
      <xsl:for-each select="step">
        <li>
          <p><xsl:value-of select="instruction"/></p>
          <pre><code><xsl:value-of select="code"/></code></pre>
        </li>
      </xsl:for-each>
    </ol>
  </section>
</xsl:template>

<xsl:template match="basic-usage|advanced-features|input-handling-and-validation|output-and-formatting|plugin-system|cross-platform-compatibility|error-handling-and-logging">
  <section id="{name()}" class="section">
    <h2>
      <xsl:call-template name="get-icon">
        <xsl:with-param name="section" select="name()"/>
      </xsl:call-template>
      <xsl:value-of select="translate(name(), '-', ' ')"/>
    </h2>
    <xsl:for-each select="section">
      <div class="subsection">
        <h3><xsl:value-of select="@name"/></h3>
        <p><xsl:value-of select="description"/></p>
        <xsl:if test="example">
          <div class="example">
            <h4>Example:</h4>
            <pre><code><xsl:value-of select="example/code"/></code></pre>
          </div>
        </xsl:if>
      </div>
    </xsl:for-each>
  </section>
</xsl:template>

<xsl:template match="best-practices-and-tips">
  <section id="best-practices-and-tips" class="section">
    <h2><i class="fas fa-lightbulb icon"></i>Best Practices and Tips</h2>
    <xsl:for-each select="section">
      <div class="subsection">
        <h3><xsl:value-of select="@name"/></h3>
        <ul>
          <xsl:for-each select="tip">
            <li><i class="fas fa-check-circle icon"></i><xsl:value-of select="."/></li>
          </xsl:for-each>
        </ul>
      </div>
    </xsl:for-each>
  </section>
</xsl:template>

<xsl:template match="api-reference">
  <section id="api-reference" class="section">
    <h2><i class="fas fa-book icon"></i>API Reference</h2>
    <xsl:for-each select="class">
      <div class="subsection">
        <h3><xsl:value-of select="@name"/></h3>
        <xsl:for-each select="method">
          <div class="method">
            <h4><xsl:value-of select="@name"/></h4>
            <p><xsl:value-of select="description"/></p>
            <h5>Parameters:</h5>
            <ul>
              <xsl:for-each select="parameters/param">
                <li><span class="parameter"><xsl:value-of select="@name"/></span>: <xsl:value-of select="."/></li>
              </xsl:for-each>
            </ul>
            <p><strong>Returns:</strong> <xsl:value-of select="returns"/></p>
          </div>
        </xsl:for-each>
      </div>
    </xsl:for-each>
  </section>
</xsl:template>

<xsl:template match="examples">
  <section id="examples" class="section">
    <h2><i class="fas fa-code icon"></i>Examples</h2>
    <xsl:for-each select="example">
      <div class="subsection">
        <h3><xsl:value-of select="@name"/></h3>
        <p><xsl:value-of select="description"/></p>
        <div class="example">
          <pre><code><xsl:value-of select="code"/></code></pre>
        </div>
      </div>
    </xsl:for-each>
  </section>
</xsl:template>

<xsl:template match="troubleshooting">
  <section id="troubleshooting" class="section">
    <h2><i class="fas fa-wrench icon"></i>Troubleshooting</h2>
    <xsl:for-each select="common-issue">
      <div class="subsection">
        <h3><i class="fas fa-exclamation-circle icon"></i><xsl:value-of select="problem"/></h3>
        <ol>
          <xsl:for-each select="solution/step">
            <li><xsl:value-of select="."/></li>
          </xsl:for-each>
        </ol>
      </div>
    </xsl:for-each>
  </section>
</xsl:template>

<xsl:template match="faq">
  <section id="faq" class="section">
    <h2><i class="fas fa-question-circle icon"></i>FAQ</h2>
    <xsl:for-each select="question">
      <div class="subsection">
        <h3><xsl:value-of select="q"/></h3>
        <p><xsl:value-of select="a"/></p>
      </div>
    </xsl:for-each>
  </section>
</xsl:template>

<xsl:template match="contributing">
  <section id="contributing" class="section">
    <h2><i class="fas fa-hands-helping icon"></i>Contributing</h2>
    <xsl:for-each select="section">
      <div class="subsection">
        <h3><xsl:value-of select="@name"/></h3>
        <xsl:choose>
          <xsl:when test="@name = 'Development Setup' or @name = 'Submitting Pull Requests'">
            <ol class="setup-steps">
              <xsl:for-each select="step">
                <li>
                  <xsl:value-of select="."/>
                  <xsl:if test="substep">
                    <ul class="substeps">
                      <xsl:for-each select="substep">
                        <li><xsl:value-of select="."/></li>
                      </xsl:for-each>
                    </ul>
                  </xsl:if>
                </li>
              </xsl:for-each>
            </ol>
          </xsl:when>
          <xsl:otherwise>
            <ul class="contribution-list">
              <xsl:for-each select="item|instruction">
                <li><i class="fas fa-check icon"></i><xsl:value-of select="."/></li>
              </xsl:for-each>
            </ul>
          </xsl:otherwise>
        </xsl:choose>
      </div>
    </xsl:for-each>
  </section>
</xsl:template>

<xsl:template match="changelog">
  <section id="changelog" class="section">
    <h2><i class="fas fa-history icon"></i>Changelog</h2>
    <xsl:for-each select="version">
      <div class="subsection">
        <h3>Version <xsl:value-of select="@number"/> (<xsl:value-of select="release-date"/>)</h3>
        <ul>
          <xsl:for-each select="changes/item">
            <li><i class="fas fa-caret-right icon"></i><xsl:value-of select="."/></li>
          </xsl:for-each>
        </ul>
      </div>
    </xsl:for-each>
  </section>
</xsl:template>

<xsl:template match="license">
  <section id="license" class="section">
    <h2><i class="fas fa-gavel icon"></i>License</h2>
    <h3><xsl:value-of select="name"/></h3>
    <pre><code><xsl:value-of select="summary"/></code></pre>
  </section>
</xsl:template>

</xsl:stylesheet>