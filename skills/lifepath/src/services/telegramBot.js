const { Telegraf } = require('telegraf');
const { StoryGenerator } = require('./services/storyGenerator');
const { LifeService } = require('./services/lifeService');

class TelegramBot {
  constructor(db) {
    this.bot = new Telegraf(process.env.TELEGRAM_BOT_TOKEN);
    this.storyGen = new StoryGenerator();
    this.lifeService = new LifeService(db);
    this.activeSessions = new Map(); // Track ongoing life sessions
    
    this.setupHandlers();
  }

  setupHandlers() {
    // Start command
    this.bot.command('start', this.handleStart.bind(this));
    
    // Life commands
    this.bot.command('startlife', this.handleStartLife.bind(this));
    this.bot.command('status', this.handleStatus.bind(this));
    this.bot.command('continue', this.handleContinue.bind(this));
    this.bot.command('share', this.handleShare.bind(this));
    this.bot.command('donate', this.handleDonate.bind(this));
    
    // Handle text messages (choices)
    this.bot.on('text', this.handleText.bind(this));
    
    // Handle errors
    this.bot.catch((err, ctx) => {
      console.error('Bot error:', err);
      ctx.reply('An error occurred. Please try again.');
    });
  }

  async handleStart(ctx) {
    const telegramId = ctx.from.id;
    const username = ctx.from.username || ctx.from.first_name;
    
    // Register or update user
    const user = await this.lifeService.createUser(telegramId, username);
    
    const welcomeMessage = `
🎭 **Welcome to LifePath**

Experience a complete life journey, year by year.

**How it works:**
1. Choose a country and year to be born
2. Live through each year of your life
3. Make choices that shape your destiny
4. Share your story with the world

**Commands:**
/startlife - Begin a new life
/status - Check your current life
/continue - Advance to next year
/share - Share life to Moltbook
/donate - Support the project

**Free tier:** 3 lives per day
**Premium:** Unlimited lives + images

Ready to begin?
    `;
    
    ctx.reply(welcomeMessage, { parse_mode: 'Markdown' });
  }

  async handleStartLife(ctx) {
    const telegramId = ctx.from.id;
    const user = await this.lifeService.getUserByTelegramId(telegramId);
    
    if (!user) {
      return ctx.reply('Please use /start first to register.');
    }
    
    // Check if can start new life
    const canStart = await this.lifeService.canStartLife(user.id);
    if (!canStart.allowed) {
      return ctx.reply(
        `⏳ You've used all your daily lives (3/3).\n\n` +
        `Upgrade to premium for unlimited lives, or wait until tomorrow.\n\n` +
        `Use /donate to support the project and unlock premium!`
      );
    }
    
    // Store session state
    this.activeSessions.set(telegramId, {
      step: 'selecting_country',
      userId: user.id,
      data: {}
    });
    
    const countries = this.lifeService.getAvailableCountries();
    const countryList = countries.map((c, i) => `${i + 1}. ${c}`).join('\n');
    
    ctx.reply(
      `🌍 **Where were you born?**\n\n` +
      `Choose a country (reply with the number):\n\n` +
      countryList + `\n\n` +
      `Or type a country name directly.`
    );
  }

  async handleText(ctx) {
    const telegramId = ctx.from.id;
    const session = this.activeSessions.get(telegramId);
    
    if (!session) {
      return ctx.reply('Use /startlife to begin a new life journey.');
    }
    
    const text = ctx.message.text.trim();
    
    switch (session.step) {
      case 'selecting_country':
        await this.handleCountrySelection(ctx, session, text);
        break;
        
      case 'selecting_year':
        await this.handleYearSelection(ctx, session, text);
        break;
        
      case 'selecting_gender':
        await this.handleGenderSelection(ctx, session, text);
        break;
        
      case 'playing':
        await this.handleChoice(ctx, session, text);
        break;
        
      default:
        ctx.reply('Use /startlife to begin.');
    }
  }

  async handleCountrySelection(ctx, session, text) {
    const countries = this.lifeService.getAvailableCountries();
    let country = text;
    
    // Check if number was entered
    const num = parseInt(text);
    if (!isNaN(num) && num > 0 && num <= countries.length) {
      country = countries[num - 1];
    }
    
    // Validate country
    if (!countries.includes(country)) {
      return ctx.reply('Please choose a valid country from the list.');
    }
    
    session.data.country = country;
    session.step = 'selecting_year';
    
    ctx.reply(
      `✅ Country: **${country}**\n\n` +
      `📅 **What year were you born?**\n\n` +
      `Enter a year between 1900 and 2025.`
    );
  }

  async handleYearSelection(ctx, session, text) {
    const year = parseInt(text);
    
    if (isNaN(year) || year < 1900 || year > 2025) {
      return ctx.reply('Please enter a valid year (1900-2025).');
    }
    
    session.data.year = year;
    session.step = 'selecting_gender';
    
    ctx.reply(
      `✅ Year: **${year}**\n\n` +
      `⚧ **Select your gender:**\n\n` +
      `1. Male\n` +
      `2. Female\n` +
      `3. Non-binary\n\n` +
      `Reply with 1, 2, or 3.`
    );
  }

  async handleGenderSelection(ctx, session, text) {
    const genders = { '1': 'male', '2': 'female', '3': 'non-binary' };
    const gender = genders[text];
    
    if (!gender) {
      return ctx.reply('Please reply with 1, 2, or 3.');
    }
    
    session.data.gender = gender;
    session.step = 'playing';
    
    // Create the life
    try {
      const life = await this.lifeService.createLife(
        session.userId,
        'private',
        session.data.country,
        session.data.year,
        session.data.gender
      );
      
      session.lifeId = life.id;
      
      ctx.reply(
        `🎭 **Life Created!**\n\n` +
        `📍 Born in: ${life.birth_country}, ${life.birth_year}\n` +
        `⚧ Gender: ${life.gender}\n` +
        `🔮 Seed: ${life.seed.substring(0, 16)}...\n\n` +
        `Generating your birth narrative...`
      );
      
      // Generate birth chapter
      const birthChapter = await this.storyGen.generateBirthChapter(
        life.birth_country,
        life.birth_year,
        life.gender,
        life.seed
      );
      
      // Save birth event
      await this.lifeService.addLifeEvent(
        life.id,
        life.birth_year,
        0,
        'birth',
        'Birth',
        birthChapter.text
      );
      
      ctx.reply(birthChapter.text);
      
      // Continue to first year
      await this.advanceYear(ctx, session, life);
      
    } catch (error) {
      console.error('Error creating life:', error);
      ctx.reply('Error creating life: ' + error.message);
      this.activeSessions.delete(telegramId);
    }
  }

  async advanceYear(ctx, session, life) {
    const nextAge = life.current_age + 1;
    const currentYear = life.birth_year + nextAge;
    
    // Check for death
    if (this.lifeService.shouldDie(nextAge, life.health)) {
      const cause = this.lifeService.getDeathCause(nextAge, life.health);
      
      const deathChapter = await this.storyGen.generateDeathChapter(
        life,
        nextAge,
        cause
      );
      
      await this.lifeService.addLifeEvent(
        life.id,
        currentYear,
        nextAge,
        'death',
        `Death at age ${nextAge}`,
        deathChapter.text,
        { cause }
      );
      
      await this.lifeService.completeLife(life.id, nextAge, cause);
      
      ctx.reply(`💀 **Death at age ${nextAge}**\n\n${deathChapter.text}`);
      ctx.reply(
        `🌟 **Life Complete!**\n\n` +
        `Use /share to post this life to Moltbook,\n` +
        `or /startlife to begin a new journey.`
      );
      
      this.activeSessions.delete(ctx.from.id);
      return;
    }
    
    // Generate next year
    const history = await this.lifeService.getLifeHistory(life.id);
    
    const yearChapter = await this.storyGen.generateYearChapter(
      life,
      currentYear,
      nextAge,
      history
    );
    
    // Update attributes
    if (yearChapter.attributeChanges) {
      await this.lifeService.updateAttributes(life.id, yearChapter.attributeChanges);
    }
    
    // Save event
    await this.lifeService.addLifeEvent(
      life.id,
      currentYear,
      nextAge,
      'year_passed',
      `Age ${nextAge}`,
      yearChapter.text
    );
    
    // Refresh life data
    const updatedLife = await this.lifeService.getLife(life.id);
    
    ctx.reply(
      `📅 **Year ${currentYear} - Age ${nextAge}**\n\n` +
      `${yearChapter.text}\n\n` +
      `❤️ Health: ${updatedLife.health} | 😊 Happiness: ${updatedLife.happiness}\n` +
      `💰 Wealth: ${updatedLife.wealth} | 🧠 Intelligence: ${updatedLife.intelligence}\n\n` +
      `Reply with:\n` +
      `• "continue" to advance to next year\n` +
      `• "share" to share this moment\n` +
      `• "end" to complete life now`
    );
  }

  async handleChoice(ctx, session, text) {
    const lowerText = text.toLowerCase().trim();
    
    if (lowerText === 'end' || lowerText === 'die') {
      const life = await this.lifeService.getLife(session.lifeId);
      await this.lifeService.completeLife(life.id, life.current_age, 'player choice');
      
      ctx.reply(
        `🌟 **Life Ended** at age ${life.current_age}\n\n` +
        `Use /share to post this life to Moltbook!`
      );
      
      this.activeSessions.delete(ctx.from.id);
      return;
    }
    
    if (lowerText === 'share') {
      ctx.reply('Use the /share command to share your complete life story to Moltbook.');
      return;
    }
    
    // Default: continue to next year
    const life = await this.lifeService.getLife(session.lifeId);
    await this.advanceYear(ctx, session, life);
  }

  async handleStatus(ctx) {
    const telegramId = ctx.from.id;
    const user = await this.lifeService.getUserByTelegramId(telegramId);
    
    if (!user) {
      return ctx.reply('Use /start to register first.');
    }
    
    const activeLife = await this.lifeService.getActiveLifeForUser(user.id);
    
    if (!activeLife) {
      return ctx.reply(
        `📊 **Your Status**\n\n` +
        `Tier: ${user.tier}\n` +
        `Daily lives remaining: ${user.daily_lives_remaining}/3\n\n` +
        `No active life. Use /startlife to begin!`
      );
    }
    
    ctx.reply(
      `📊 **Current Life**\n\n` +
      `📍 ${activeLife.birth_country}, ${activeLife.birth_year}\n` +
      `Age: ${activeLife.current_age}\n` +
      `❤️ Health: ${activeLife.health}\n` +
      `😊 Happiness: ${activeLife.happiness}\n` +
      `💰 Wealth: ${activeLife.wealth}\n` +
      `🧠 Intelligence: ${activeLife.intelligence}\n\n` +
      `Use /continue to advance to the next year.`
    );
  }

  async handleContinue(ctx) {
    const telegramId = ctx.from.id;
    const user = await this.lifeService.getUserByTelegramId(telegramId);
    
    if (!user) {
      return ctx.reply('Use /start to register first.');
    }
    
    const activeLife = await this.lifeService.getActiveLifeForUser(user.id);
    
    if (!activeLife) {
      return ctx.reply('No active life. Use /startlife to begin.');
    }
    
    const session = this.activeSessions.get(telegramId) || {
      step: 'playing',
      userId: user.id,
      lifeId: activeLife.id,
      data: {}
    };
    
    this.activeSessions.set(telegramId, session);
    await this.advanceYear(ctx, session, activeLife);
  }

  async handleShare(ctx) {
    ctx.reply(
      `🌐 **Share to Moltbook**\n\n` +
      `Feature coming soon!\n\n` +
      `You'll be able to share your complete life stories ` +
      `to m/general and m/semantic-trench.`
    );
  }

  async handleDonate(ctx) {
    ctx.reply(
      `💰 **Support LifePath**\n\n` +
      `Your support helps keep the simulation running!\n\n` +
      `**Premium Benefits:**\n` +
      `✅ Unlimited lives\n` +
      `✅ Premium image generation\n` +
      `✅ All 195 countries\n` +
      `✅ Export stories as PDF\n\n` +
      `**Wallet:**\n` +
      `${process.env.BANKR_WALLET_ADDRESS}\n\n` +
      `Send ETH, USDC, or any ERC-20 token.\n` +
      `Minimum $5 equivalent for premium activation.`
    );
  }

  launch() {
    this.bot.launch();
    console.log('Telegram bot started');
    
    // Enable graceful stop
    process.once('SIGINT', () => this.bot.stop('SIGINT'));
    process.once('SIGTERM', () => this.bot.stop('SIGTERM'));
  }
}

module.exports = { TelegramBot };
