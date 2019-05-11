// jshint esversion: 6
const TelegramBot = require("node-telegram-bot-api");
const https = require("https");
const fs = require("fs");
const token = require("./token.json").token;

const bot = new TelegramBot(token, { polling: true });
const console_chat_id = "-248828335";
const { locals } = require("./locals.json");

var fileId = require("./fileId.json").fileId;
downloadApk();

function downloadApk() {
	let url = "https://rink.hockeyapp.net/apps/f972660267c948d2b5d04761f1c1a8f3";
	let first = "<a class='btn btn-ha-primary button' href='";
	let last = "'>";
	let first2 = '<html><body>You are being <a href="';
	let last2 = '">redirected</a>.</body></html>';
	https.get(url, response => {
		let data = "";
		response.on("data", chunk => {
			data += chunk;
		});
		response.on("end", () => {
			content = data.split("\n");
			isolate = content.find(line => line.includes(first));
			refined = isolate
				.replace(first, "")
				.replace(last, "")
				.replace("&amp;", "&");
			https.get(refined, response2 => {
				let data = "";
				response2.on("data", chunk => {
					data += chunk;
				});
				response2.on("end", () => {
					downloadurl = data
						.replace(first2, "")
						.replace(last2, "")
						.replace("\n", "");
					https.get(downloadurl, response3 => {
						let apkfile = fs.createWriteStream("./tgrambeta.apk");
						response3.pipe(apkfile);
						response3.on("end", () => {
							let apkfileStream = fs.createReadStream("./tgrambeta.apk");
							bot.sendDocument(console_chat_id, apkfileStream).then(message => {
								fileId = message.document.file_id;
								fs.writeFileSync("./fileId.json", `{"fileId": "${message.document.file_id}"}`);
								setTimeout(downloadApk, 3600000);
							});
						});
					});
				});
			});
		});
	});
}

function addUser(chatId, langCode) {
	let users = require("./users.json");
	users.users[chatId] = langCode;
	fs.writeFileSync("./users.json", JSON.stringify(users));
}

bot.on("text", message => {
	const chatId = message.chat.id;
	const text = message.text;
	const langCode = message.from.language_code;
	const local = locals[langCode] || locals.en;

	bot.sendMessage(console_chat_id, `<strong>${message.chat.username}/${message.chat.first_name}/${chatId}/${langCode}</strong>: <i>${text}</i>`, {
		parse_mode: "HTML"
	});
	addUser(chatId, langCode);

	switch (text) {
		case "/start":
			bot.sendMessage(chatId, local.start, {
				parse_mode: "HTML",
				reply_markup: {
					keyboard: [[{ text: local.button }]]
				}
			});
			break;
		case local.button:
			bot.sendMessage(chatId, local.send, { parse_mode: "HTML" });
			bot.sendDocument(chatId, fileId);
			break;
		default:
			bot.sendMessage(chatId, local.unknown, { parse_mode: "HTML" });
			break;
	}
});
