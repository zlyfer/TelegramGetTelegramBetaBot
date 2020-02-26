// jshint esversion: 6
const TelegramBot = require("node-telegram-bot-api");
const https = require("https");
const fs = require("fs");
const token = require("./token.json").token;

const bot = new TelegramBot(token, { polling: true });
const console_chat_id = "-248828335";
const { locals } = require("./locals.json");
var { users } = require("./users.json");

var fileId = require("./fileId.json").fileId;
downloadApk();
setInterval(function() {
  downloadApk();
}, 21600000);

function downloadApk() {}

function addUser(chatId, langCode) {
  users[chatId] = langCode;
  fs.writeFileSync("./users.json", JSON.stringify({ users }));
}

bot.on("text", message => {
  const chatId = message.chat.id;
  const text = message.text;
  const langCode = users[chatId] || message.from.language_code;
  const local = locals[langCode] || locals.en;

  bot.sendMessage(
    console_chat_id,
    `<strong>${message.chat.username}/${message.chat.first_name}/${chatId}/${langCode}</strong>: <i>${text}</i>`,
    {
      parse_mode: "HTML"
    }
  );
  addUser(chatId, langCode);

  // TEMP:
  bot.sendMessage(chatId, `This bot only serves a <strong>outdated version</strong> of Telgram Beta because the download source changed.\nYou will probably still be able to update via the app itself.\nIf you want to download the newest Beta version by yourself head over to: <a href="https://install.appcenter.ms/users/drklo-2kb-ghpo/apps/telegram-beta-2/distribution_groups/all-users-of-telegram-beta-2">App Center</a>\nSorry for the inconvenience, I will try to re-add the automatic download when I have time. Feel free to checkout the <a href="https://github.com/zlyfer/TelegramGetTelegramBetaBot/tree/nodejs">GitHub Repo</a> to contibute.`, { parse_mode: "HTML" });

  switch (text) {
    case "/start":
      bot.sendMessage(
        chatId,
        Object.keys(locals)
          .map(lang => {
            return `${locals[lang].flag} ${locals[lang].select}`;
          })
          .join("\n"),
        {
          parse_mode: "HTML",
          reply_markup: {
            keyboard: Object.keys(locals).map(lang => {
              return [{ text: `${locals[lang].flag} ${locals[lang].languagename}` }];
            })
          }
        }
      );
      break;
    case local.button:
      bot.sendMessage(chatId, local.send, { parse_mode: "HTML" });
      bot.sendDocument(chatId, fileId);
      break;
    default:
      let lang = Object.keys(locals)
        .map(lang => {
          return locals[lang];
        })
        .find(lang => `${lang.flag} ${lang.languagename}` == text);
      if (lang) {
        addUser(chatId, lang.code);
        bot.sendMessage(chatId, locals[lang.code].start, {
          parse_mode: "HTML",
          reply_markup: {
            keyboard: [[{ text: locals[lang.code].button }]]
          }
        });
      } else bot.sendMessage(chatId, local.unknown, { parse_mode: "HTML" });
      break;
  }
});
