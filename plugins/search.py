"""
Search commands - Google, Wikipedia, YouTube, etc.
"""
from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from logger import LOGGER
import aiohttp
import urllib.parse

@Client.on_message(filters.command("google"))
async def google_search(client: Client, message: Message):
    """Google search"""
    try:
        if len(message.command) < 2:
            await message.reply_text("❌ Usage: /google [query]")
            return
        
        query = " ".join(message.command[1:])
        encoded_query = urllib.parse.quote(query)
        
        search_url = f"https://www.google.com/search?q={encoded_query}"
        
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("🔍 Search on Google", url=search_url)]
        ])
        
        await message.reply_text(
            f"🔍 **Google Search**\n\n"
            f"Query: `{query}`\n\n"
            f"Click the button below to search:",
            reply_markup=keyboard
        )
        
    except Exception as e:
        await message.reply_text(f"❌ Error: {str(e)}")
        LOGGER.error(f"Google search error: {e}")

@Client.on_message(filters.command("wiki"))
async def wikipedia_search(client: Client, message: Message):
    """Wikipedia search"""
    try:
        if len(message.command) < 2:
            await message.reply_text("❌ Usage: /wiki [query]")
            return
        
        query = " ".join(message.command[1:])
        
        status = await message.reply_text("🔍 Searching Wikipedia...")
        
        # Wikipedia API
        url = f"https://en.wikipedia.org/api/rest_v1/page/summary/{urllib.parse.quote(query)}"
        
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                if response.status == 200:
                    data = await response.json()
                    
                    # Check if the page type is valid (not a disambiguation or missing page)
                    page_type = data.get('type', '')
                    if page_type == 'disambiguation':
                        await status.edit_text(f"❌ '{query}' is a disambiguation page. Please be more specific!")
                        return
                    
                    title = data.get('title', 'Not Found')
                    extract = data.get('extract', 'No information available.')
                    page_url = data.get('content_urls', {}).get('desktop', {}).get('page', '')
                    thumbnail = data.get('thumbnail', {}).get('source', '')
                    
                    # Check if we got meaningful content
                    if not extract or not extract.strip():
                        await status.edit_text(f"❌ No information found for '{query}'!")
                        return
                    
                    text = f"📚 **Wikipedia - {title}**\n\n{extract}"
                    
                    if len(text) > 4096:
                        text = text[:4090] + "..."
                    
                    keyboard = InlineKeyboardMarkup([
                        [InlineKeyboardButton("📖 Read More", url=page_url)]
                    ]) if page_url else None
                    
                    if thumbnail:
                        try:
                            await status.delete()
                            await message.reply_photo(
                                thumbnail,
                                caption=text,
                                reply_markup=keyboard
                            )
                        except Exception as photo_err:
                            LOGGER.error(f"Failed to send photo: {photo_err}")
                            await status.edit_text(text, reply_markup=keyboard)
                    else:
                        await status.edit_text(text, reply_markup=keyboard)
                elif response.status == 404:
                    await status.edit_text(f"❌ No Wikipedia page found for '{query}'!")
                else:
                    await status.edit_text(f"❌ Error searching Wikipedia (Status: {response.status})")
        
    except Exception as e:
        await message.reply_text(f"❌ Error: {str(e)}")
        LOGGER.error(f"Wiki search error: {e}")

@Client.on_message(filters.command("yt"))
async def youtube_search(client: Client, message: Message):
    """YouTube search"""
    try:
        if len(message.command) < 2:
            await message.reply_text("❌ Usage: /yt [query]")
            return
        
        query = " ".join(message.command[1:])
        encoded_query = urllib.parse.quote(query)
        
        search_url = f"https://www.youtube.com/results?search_query={encoded_query}"
        
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("🎥 Search on YouTube", url=search_url)]
        ])
        
        await message.reply_text(
            f"🎥 **YouTube Search**\n\n"
            f"Query: `{query}`\n\n"
            f"Click the button below to search:",
            reply_markup=keyboard
        )
        
    except Exception as e:
        await message.reply_text(f"❌ Error: {str(e)}")

@Client.on_message(filters.command("tr"))
async def translate_text(client: Client, message: Message):
    """Translate text using Google Translate"""
    try:
        if len(message.command) < 3:
            await message.reply_text(
                "❌ Usage: /tr [language_code] [text]\n\n"
                "Example: /tr es Hello World\n\n"
                "Common codes: en, es, fr, de, it, pt, ru, ja, ko, zh"
            )
            return
        
        target_lang = message.command[1]
        text_to_translate = " ".join(message.command[2:])
        
        # Simple translation API (you can use Google Translate API for better results)
        url = f"https://translate.googleapis.com/translate_a/single?client=gtx&sl=auto&tl={target_lang}&dt=t&q={urllib.parse.quote(text_to_translate)}"
        
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                if response.status == 200:
                    data = await response.json()
                    
                    translated = ""
                    for item in data[0]:
                        if item[0]:
                            translated += item[0]
                    
                    await message.reply_text(
                        f"🌐 **Translation**\n\n"
                        f"**Original:** {text_to_translate}\n\n"
                        f"**Translated ({target_lang}):** {translated}"
                    )
                else:
                    await message.reply_text("❌ Translation failed!")
        
    except Exception as e:
        await message.reply_text(f"❌ Error: {str(e)}")
        LOGGER.error(f"Translation error: {e}")

@Client.on_message(filters.command("weather"))
async def get_weather(client: Client, message: Message):
    """Get weather information"""
    try:
        if len(message.command) < 2:
            await message.reply_text("❌ Usage: /weather [city]")
            return
        
        city = " ".join(message.command[1:])
        
        # You can use OpenWeatherMap API or other weather APIs
        # This is a placeholder - you need to add your API key
        
        await message.reply_text(
            f"🌤️ **Weather in {city}**\n\n"
            f"Note: Add OpenWeatherMap API key to config for real data\n\n"
            f"Visit: https://openweathermap.org/api"
        )
        
    except Exception as e:
        await message.reply_text(f"❌ Error: {str(e)}")

@Client.on_message(filters.command("imdb"))
async def imdb_search(client: Client, message: Message):
    """Search IMDB"""
    try:
        if len(message.command) < 2:
            await message.reply_text("❌ Usage: /imdb [movie/series name]")
            return
        
        query = " ".join(message.command[1:])
        
        # OMDB API (you need API key)
        await message.reply_text(
            f"🎬 **IMDB Search: {query}**\n\n"
            f"Note: Add OMDB API key to config for real data\n\n"
            f"Get API key at: http://www.omdbapi.com/apikey.aspx"
        )
        
    except Exception as e:
        await message.reply_text(f"❌ Error: {str(e)}")

@Client.on_message(filters.command("define"))
async def define_word(client: Client, message: Message):
    """Define a word"""
    try:
        if len(message.command) < 2:
            await message.reply_text("❌ Usage: /define [word]")
            return
        
        word = message.command[1]
        
        # Dictionary API
        url = f"https://api.dictionaryapi.dev/api/v2/entries/en/{word}"
        
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                if response.status == 200:
                    data = await response.json()
                    
                    if data:
                        entry = data[0]
                        word_text = entry.get('word', word).capitalize()
                        phonetic = entry.get('phonetic', '')
                        
                        text = f"📖 **{word_text}**"
                        if phonetic:
                            text += f" _{phonetic}_"
                        text += "\n\n"
                        
                        meanings = entry.get('meanings', [])
                        for i, meaning in enumerate(meanings[:3], 1):  # Limit to 3
                            part_of_speech = meaning.get('partOfSpeech', '')
                            definitions = meaning.get('definitions', [])
                            
                            if definitions:
                                text += f"**{part_of_speech.capitalize()}:**\n"
                                for j, definition in enumerate(definitions[:2], 1):  # Limit to 2
                                    def_text = definition.get('definition', '')
                                    text += f"{j}. {def_text}\n"
                                    
                                    example = definition.get('example')
                                    if example:
                                        text += f"   _Example: {example}_\n"
                                text += "\n"
                        
                        await message.reply_text(text)
                else:
                    await message.reply_text(f"❌ Could not find definition for '{word}'")
        
    except Exception as e:
        await message.reply_text(f"❌ Error: {str(e)}")
        LOGGER.error(f"Define error: {e}")