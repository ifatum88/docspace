// Pages
[
    {
        name: 'Архитектура',
        order: 0,
        slug: 'arch',
        child: [],
        doc: "",
        author: "Дима Гич",
        updater: "Дима Гич",
        created: new Date(),
        updated: new Date()
    },
    {
        name: 'C4 diagram',
        order: 0,
        slug: 'c4-d',
        child: [],
        doc: "",
        author: "Дима Гич",
        updater: "Дима Гич",
        created: new Date(),
        updated: new Date()
    },
    {
        name: 'API Contacts',
        order: 1,
        slug: 'api-c',
        child: [],
        doc: "",
        author: "Дима Гич",
        updater: "Дима Гич",
        created: new Date(),
        updated: new Date()
    },
    {
        name: 'Sequence diagram',
        order: 2,
        slug: 'sd',
        child: [],
        doc: "",
        author: "Дима Гич",
        updater: "Дима Гич",
        created: new Date(),
        updated: new Date()
    },
    {
        name: 'PDM',
        order: 3,
        slug: 'pdm',
        child: [],
        doc: "",
        author: "Дима Гич",
        updater: "Дима Гич",
        created: new Date(),
        updated: new Date()
    },
    {
        name: 'Документация',
        order: 0,
        slug: 'docs',
        child: [],
        doc: "",
        author: "Дима Гич",
        updater: "Дима Гич",
        created: new Date(),
        updated: new Date()
    },
    {
        name: 'Установка',
        order: 0,
        slug: 'install',
        child: [],
        doc: "",
        author: "Дима Гич",
        updater: "Дима Гич",
        created: new Date(),
        updated: new Date()
    },
    {
        name: 'Конфигурации',
        order: 1,
        slug: 'conf',
        child: [],
        doc: "",
        author: "Дима Гич",
        updater: "Дима Гич",
        created: new Date(),
        updated: new Date()
    },
    {
        name: 'Use-cases',
        order: 2,
        slug: 'uc',
        child: [],
        doc: "",
        author: "Дима Гич",
        updater: "Дима Гич",
        created: new Date(),
        updated: new Date()
    },
]

// Апдейт child
// Архитектура
db.pages.updateOne(
    { _id: ObjectId("680b347c3c4fbae5dac48217") },
    { $set: { child: [
        ObjectId("680b347c3c4fbae5dac48218"), // C4 diagram
        ObjectId("680b347c3c4fbae5dac48219"), // API Contacts
        ObjectId("680b347c3c4fbae5dac4821a"), // Sequence diagram
        ObjectId("680b347c3c4fbae5dac4821b")  // PDM
    ]}}
  );
  
  // Документация
  db.pages.updateOne(
    { _id: ObjectId("680b347c3c4fbae5dac4821c") },
    { $set: { child: [
        ObjectId("680b347c3c4fbae5dac4821d"), // Установка
        ObjectId("680b347c3c4fbae5dac4821e"), // Конфигурации
        ObjectId("680b347c3c4fbae5dac4821f")  // Use-cases
    ]}}
  );

  // Docs
  
  [
    {
        type: "markdown",
        content: "# Markdown syntax guide\n\n## Headers\n\n# This is a Heading h1\n## This is a Heading h2\n###### This is a Heading h6\n\n## Emphasis\n\n*This text will be italic*  \n_This will also be italic_\n\n**This text will be bold**  \n__This will also be bold__\n\n_You **can** combine them_\n\n## Lists\n\n### Unordered\n\n* Item 1\n* Item 2\n* Item 2a\n* Item 2b\n    * Item 3a\n    * Item 3b\n\n### Ordered\n\n1. Item 1\n2. Item 2\n3. Item 3\n    1. Item 3a\n    2. Item 3b\n\n## Images\n\n![This is an alt text.](https://markdownlivepreview.com/image/sample.webp \"This is a sample image.\")\n\n## Links\n\nYou may be using [Markdown Live Preview](https://markdownlivepreview.com/).\n\n## Blockquotes\n\n> Markdown is a lightweight markup language with plain-text-formatting syntax, created in 2004 by John Gruber with Aaron Swartz.\n>\n>> Markdown is often used to format readme files, for writing messages in online discussion forums, and to create rich text using a plain text editor.\n\n## Tables\n\n| Left columns  | Right columns |\n| ------------- |:-------------:|\n| left foo      | right foo     |\n| left bar      | right bar     |\n| left baz      | right baz     |\n\n## Blocks of code\n\n```\nlet message = 'Hello world';\nalert(message);\n```\n\n## Inline code\n\nThis web site is using `markedjs/marked`.\n",
        author: "Дима Гич",
        created: new Date(),
        updated: new Date(),
        updater: "Дима Гич"
      },
      {
        type: "markdown",
        content: "# Markdown syntax guide\n\n## Headers\n\n# This is a Heading h1\n## This is a Heading h2\n###### This is a Heading h6\n\n## Emphasis\n\n*This text will be italic*  \n_This will also be italic_\n\n**This text will be bold**  \n__This will also be bold__\n\n_You **can** combine them_\n\n## Lists\n\n### Unordered\n\n* Item 1\n* Item 2\n* Item 2a\n* Item 2b\n    * Item 3a\n    * Item 3b\n\n### Ordered\n\n1. Item 1\n2. Item 2\n3. Item 3\n    1. Item 3a\n    2. Item 3b\n\n## Images\n\n![This is an alt text.](https://markdownlivepreview.com/image/sample.webp \"This is a sample image.\")\n\n## Links\n\nYou may be using [Markdown Live Preview](https://markdownlivepreview.com/).\n\n## Blockquotes\n\n> Markdown is a lightweight markup language with plain-text-formatting syntax, created in 2004 by John Gruber with Aaron Swartz.\n>\n>> Markdown is often used to format readme files, for writing messages in online discussion forums, and to create rich text using a plain text editor.\n\n## Tables\n\n| Left columns  | Right columns |\n| ------------- |:-------------:|\n| left foo      | right foo     |\n| left bar      | right bar     |\n| left baz      | right baz     |\n\n## Blocks of code\n\n```\nlet message = 'Hello world';\nalert(message);\n```\n\n## Inline code\n\nThis web site is using `markedjs/marked`.\n",
        author: "Дима Гич",
        created: new Date(),
        updated: new Date(),
        updater: "Дима Гич"
      },
      {
        type: "markdown",
        content: "# Document 1\nOnly text",
        author: "Дима Гич",
        created: new Date(),
        updated: new Date(),
        updater: "Дима Гич"
      },
      {
        type: "markdown",
        content: "# Document 2\nText and image\n![This is an alt text.](/image/sample.webp \"This is a sample image.\")",
        author: "Дима Гич",
        created: new Date(),
        updated: new Date(),
        updater: "Дима Гич"
      },
      {
        type: "markdown",
        content: "# Document 3\n## Tables\n\n| Left columns  | Right columns |\n| ------------- |:-------------:|\n| left foo      | right foo     |\n| left bar      | right bar     |\n| left baz      | right baz     |",
        author: "Дима Гич",
        created: new Date(),
        updated: new Date(),
        updater: "Дима Гич"
      },


      {
        type: "markdown",
        content: "# Document 1\n## Tables\n\n| Left columns  | Right columns |\n| ------------- |:-------------:|\n| left foo      | right foo     |\n| left bar      | right bar     |\n| left baz      | right baz     |",
        author: "Дима Гич",
        created: new Date(),
        updated: new Date(),
        updater: "Дима Гич"
      },
      {
        type: "html",
        content: "<h1>Заголовок блока с HTML<h1><p>Текст внутри абзаца</p>",
        author: "Дима Гич",
        created: new Date(),
        updated: new Date(),
        updater: "Дима Гич"
      },
      {
        type: "plain-text",
        content: "Просто текст",
        author: "Дима Гич",
        created: new Date(),
        updated: new Date(),
        updater: "Дима Гич"
      },
      {
        type: "plantuml",
        content: "@startuml Bob -> Alice : hello @enduml",
        author: "Иван Петров",
        created: new Date(),
        updated: new Date(),
        updater: "Федор Иванович"
      },
      {
        type: "draw.io",
        content: "rr",
        author: "Серж Горелый",
        created: new Date(),
        updated: new Date(),
        updater: "Федор Иванович"
      },
  ]