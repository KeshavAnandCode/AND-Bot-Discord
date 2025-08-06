// ✅ Discord bot to ping users with BOTH roles using a command
// 🌐 Ready for Replit deployment

const express = require('express');
const { Client, GatewayIntentBits, Partials } = require('discord.js');
const dotenv = require('dotenv');
dotenv.config();

const app = express();
const port = 3000;

// Keep-alive endpoint for UptimeRobot
app.get('/', (req, res) => {
  res.send('Bot is alive!');
});
app.listen(port, () => {
  console.log(`Keep-alive server running on http://localhost:${port}`);
});

// Discord bot setup
const client = new Client({
  intents: [
    GatewayIntentBits.Guilds,
    GatewayIntentBits.GuildMessages,
    GatewayIntentBits.MessageContent,
    GatewayIntentBits.GuildMembers,
  ],
  partials: [Partials.Channel]
});

const PREFIX = '!';

client.on('ready', () => {
  console.log(`✅ Logged in as ${client.user.tag}`);
});

client.on('messageCreate', async message => {
  if (message.author.bot) return;

  // Detect if message is in spoilers
  const isSpoilered = message.content.startsWith('||') && message.content.endsWith('||');

  // Strip spoilers if present
  const rawContent = isSpoilered ? message.content.slice(2, -2) : message.content;

  if (!rawContent.startsWith(PREFIX)) return;

  const args = rawContent.slice(PREFIX.length).trim().split(/ +/);
  const command = args.shift().toLowerCase();

  if (command === 'and') {
    const [roleName1, roleName2] = args;
    if (!roleName1 || !roleName2) {
      return message.reply('❌ Usage: `!and RoleName1 RoleName2`');
    }

    const guild = message.guild;
    await guild.members.fetch();

    const role1 = guild.roles.cache.find(r => r.name.toLowerCase() === roleName1.toLowerCase());
    const role2 = guild.roles.cache.find(r => r.name.toLowerCase() === roleName2.toLowerCase());

    if (!role1 || !role2) {
      return message.reply('❌ One or both roles not found.');
    }

    const membersWithBoth = role1.members.filter(member => member.roles.cache.has(role2.id));

    if (membersWithBoth.size === 0) {
      return message.reply('⚠️ No members have both roles.');
    }

    const mentions = membersWithBoth.map(m => `<@${m.id}>`).join(' ');
    const response = `🔔 Members with both roles:\n${mentions}`;

    message.channel.send(
      isSpoilered ? `||${response}||` : response
    );
  }
});

client.login(process.env.TOKEN);