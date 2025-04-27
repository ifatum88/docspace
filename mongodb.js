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
        created: "2025-04-25 15:54:29.920719",
        updated: "2025-04-25 15:54:29.920719"
    },
    {
        name: 'C4 diagram',
        order: 0,
        slug: 'c4-d',
        child: [],
        doc: "",
        author: "Дима Гич",
        updater: "Дима Гич",
        created: "2025-04-25 15:54:29.920719",
        updated: "2025-04-25 15:54:29.920719"
    },
    {
        name: 'API Contacts',
        order: 1,
        slug: 'api-c',
        child: [],
        doc: "",
        author: "Дима Гич",
        updater: "Дима Гич",
        created: "2025-04-25 15:54:29.920719",
        updated: "2025-04-25 15:54:29.920719"
    },
    {
        name: 'Sequence diagram',
        order: 2,
        slug: 'sd',
        child: [],
        doc: "",
        author: "Дима Гич",
        updater: "Дима Гич",
        created: "2025-04-25 15:54:29.920719",
        updated: "2025-04-25 15:54:29.920719"
    },
    {
        name: 'PDM',
        order: 3,
        slug: 'pdm',
        child: [],
        doc: "",
        author: "Дима Гич",
        updater: "Дима Гич",
        created: "2025-04-25 15:54:29.920719",
        updated: "2025-04-25 15:54:29.920719"
    },
    {
        name: 'Документация',
        order: 0,
        slug: 'docs',
        child: [],
        doc: "",
        author: "Дима Гич",
        updater: "Дима Гич",
        created: "2025-04-25 15:54:29.920719",
        updated: "2025-04-25 15:54:29.920719"
    },
    {
        name: 'Установка',
        order: 0,
        slug: 'install',
        child: [],
        doc: "",
        author: "Дима Гич",
        updater: "Дима Гич",
        created: "2025-04-25 15:54:29.920719",
        updated: "2025-04-25 15:54:29.920719"
    },
    {
        name: 'Конфигурации',
        order: 1,
        slug: 'conf',
        child: [],
        doc: "",
        author: "Дима Гич",
        updater: "Дима Гич",
        created: "2025-04-25 15:54:29.920719",
        updated: "2025-04-25 15:54:29.920719"
    },
    {
        name: 'Use-cases',
        order: 2,
        slug: 'uc',
        child: [],
        doc: "",
        author: "Дима Гич",
        updater: "Дима Гич",
        created: "2025-04-25 15:54:29.920719",
        updated: "2025-04-25 15:54:29.920719"
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
  