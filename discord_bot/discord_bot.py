import discord
import time
from sqlalchemy import create_engine, text


engine = create_engine("postgresql:///cse412_dev", echo=True, future=True)

key = 'MTA0MjUyMDg1MDI2MTM0ODQxMg.GlAvcC.4wGbuOhmyrLhBq8_MyLfeqY106jw_NgNO3fcTQ'

intents = discord.Intents.default()
intents.members = True
intents.message_content = True
client = discord.Client(intents=intents)

async def setup_server(message):
    split = message.content.split(' ')
    guild = message.guild
    discord_id = int(split[1])

    #static setup stuff
    #delete existing channels / restart server
    channels = await guild.fetch_channels()
    for chan in channels:
        print("deleted", chan.name)
        await chan.delete()
    roles = await guild.fetch_roles()
    for rol in roles:
        if rol.name == 'Admin' or rol.name == 'TA' or rol.name=='Professor':
            print("deleted", rol.name)
            await rol.delete()
    #create roles
    admin_role = await guild.create_role(name='Admin',hoist=True,color=0xde0000)
    ta_role = await guild.create_role(name='TA',hoist=True,color=0x0008000)
    prof_role = await guild.create_role(name='Professor',hoist=True,color=0x002080)

    #create categories
    moderation = await guild.create_category('Moderation')
    info_category = await guild.create_category('Information')
    text_channels = await guild.create_category('Text Channels')
    voice_channels = await guild.create_category('Voice Channels')

    await moderation.set_permissions(guild.default_role, read_messages=False, send_messages=False)
    await moderation.set_permissions(admin_role, read_messages=True, send_messages=True)

    #create channels in Information category
    welcome = await guild.create_text_channel('welcome', category=info_category)
    role_channel = await guild.create_text_channel('roles', category=info_category)
    rules_channel = await guild.create_text_channel('rules', category=info_category)
    info_channel = await guild.create_text_channel('info', category=info_category)
    announcements = await guild.create_text_channel('announcements', category=info_category)
    await guild.create_text_channel('server invites', category=text_channels)
    await guild.edit(system_channel=welcome)
    
    await info_category.set_permissions(guild.default_role, read_messages=True, send_messages=False)
    await info_category.set_permissions(admin_role, read_messages=True, send_messages=True)
    await info_category.set_permissions(ta_role, read_messages=True, send_messages=True)
    await info_category.set_permissions(prof_role, read_messages=True, send_messages=True)



    #create channels in text channels category
    await guild.create_text_channel('general', category=text_channels)
    await guild.create_text_channel('bot commands', category=text_channels)
    await guild.create_text_channel('test prep', category=text_channels)
    await guild.create_text_channel('homework help', category=text_channels)

    #create channels in voice channels category
    await guild.create_voice_channel('Lounge', category=voice_channels)
    await guild.create_voice_channel('Study Room 1', category=voice_channels)
    await guild.create_voice_channel('Study Room 2', category=voice_channels)
    afk_channel = await guild.create_voice_channel('afk-channel', category=voice_channels)
    await guild.edit(afk_channel=afk_channel)

    #create moderation channels
    await guild.create_text_channel('moderator bot commands', category=moderation)
    await guild.create_text_channel('moderator chat', category=moderation)

    #non-static setup
    #get this discord and the sections its for
    conn = engine.connect()
    results = conn.execute(text("""
                SELECT 
                Professor.name, Professor.email, Professor.phone_number, Professor.bio, Professor.website,
                Section.section_number, Section.location, Section.semester, Section.session, Section.open_seats,
                Course.subject, Course.course_number, Course.number_ext, Course.title, Course.credits, Course.general_studies, Course.description
                FROM Professor 
                INNER JOIN Teaches ON Professor.professor_id=Teaches.professor_id 
                INNER JOIN Section ON Teaches.section_number=Section.section_number
                INNER JOIN Discord_For ON Discord_For.section_number=Section.section_number
                INNER JOIN Scheduled ON Scheduled.section_number=Section.section_number
                INNER JOIN Course ON Scheduled.course_number = Course.course_number AND Scheduled.subject=Course.subject
                WHERE server_id = :id;
                        """)
                        ,
                        {'id':discord_id})
    conn.commit()
    section_role_names = []
    professor_names = []
    professor_bios = []
    for r in results:
        print(r)
        section_role_names.append(f"{r[0]} {r[10]} {r[11]} -- {r[6]} {r[7]} {r[8]} ({r[5]})")
        name = r[0]
        if name not in professor_names:
            professor_names.append(name)
            bio = f"{r[1]}\n"
            if r[2]: bio += f"{r[2]}\n"
            if r[4]: bio += f"{r[4]}\n"
            if r[3]: 
                b = "\n" + r[3].replace('<p>','').replace('</p>','')
                b = b.replace("<a>","").replace("<a href=\"", " ").replace("</a>","")
                b = b.replace("<strong>","").replace("</strong>","").replace("&nbsp","")
                b = b.replace("<em>","").replace("</em>","")
                bio += b
            professor_bios.append(bio)


    


    #delete old roles for the sections
    section_role_colors = (0x00ee00, 0xaabb00, 0xff5500, 0xaa00aa, 0x0800ff,)
    section_role_emotes = ('0️⃣', '1️⃣', '2️⃣', '3️⃣', '4️⃣', '5️⃣', '6️⃣', '7️⃣', '8️⃣', '9️⃣')
    roles = await guild.fetch_roles()
    for rol in roles:
        if rol.name in section_role_names:
            print("deleted", rol.name)
            await rol.delete()
    #create new roles for each section
    section_roles = []
    i = 0
    for role in section_role_names:
        section_roles.append(await guild.create_role(name=role,hoist=True,color=section_role_colors[i % len(section_role_colors)]))
        i+=1

    #create category + channels for each professor (voice channel for studying, homework help, chat)
    for professor in professor_names:
        cat = await guild.create_category(professor)
        await cat.set_permissions(guild.default_role, read_messages=False, send_messages=False)
        for role in section_roles:
            if role.name.startswith(professor):
                await cat.set_permissions(role, read_messages=True, send_messages=True)
                await guild.create_text_channel(role.name[len(professor):], category=cat)
        await guild.create_text_channel('homework help', category=cat)
        await guild.create_text_channel('chat', category=cat)
        await guild.create_voice_channel('Studying', category=cat)

    #info dump for class and professors
    msg = ''
    for i in range(len(professor_names)):
        msg += f'{professor_names[i]}\n'
        for y in range (len(section_roles)):
            if section_roles[y].name.startswith(professor_names[i]):
                msg += f'{section_roles[y].name}\n'
        msg += f'\n{professor_bios[i]}\n\n'
        while len(msg) > 2000:
                next_msg = msg[:2000]
                msg = msg[2000:]
                info_msg = await info_channel.send(next_msg)
                await info_msg.pin()
        info_msg = await info_channel.send(msg)
        await info_msg.pin()
        msg = ''

    #add reaction roles message in roles channel, react to it
    msg = ''
    for i,sec in enumerate(section_role_names):
        msg += f'{section_role_emotes[i]} -- {sec}\n\n'
    role_msg = await role_channel.send(msg)
    for i in range(len(section_role_names)):
        await role_msg.add_reaction(section_role_emotes[i])
    await role_msg.pin()
   
    #add default rules channel message
    rules_msg = await rules_channel.send("1. Don't spam 2.\nDon't be rude.\n3.No NSFW\n4.Don't mass ping.\n")
    await rules_msg.pin()
    print('setup')

@client.event 
async def on_ready():
    print(f'we have logged in as {client.user}')

@client.event 
async def on_message(message):
    if message.author != client.user:
        if message.content.startswith('setup'):
            await setup_server(message)
        elif message.content == 'sqltest':
            conn = engine.connect()
            results = conn.execute(text("""
                SELECT 
                Professor.name, Professor.email, Professor.phone_number, Professor.bio, Professor.website,
                Section.section_number, Section.location, Section.semester, Section.session, Section.open_seats,
                Course.subject, Course.course_number, Course.number_ext, Course.title, Course.credits, Course.general_studies, Course.description
                FROM Professor 
                INNER JOIN Teaches ON Professor.professor_id=Teaches.professor_id 
                INNER JOIN Section ON Teaches.section_number=Section.section_number
                INNER JOIN Discord_For ON Discord_For.section_number=Section.section_number
                INNER JOIN Scheduled ON Scheduled.section_number=Section.section_number
                INNER JOIN Course ON Scheduled.course_number = Course.course_number AND Scheduled.subject=Course.subject
                WHERE server_id = :id;
                        """)
                        ,
                        {'id':3})
            for r in results:
                print(r)
                await message.channel.send(str(r))
            conn.commit()
        else:
         print(message.content)
        

#TODO maybe automatically apply some roles? upon joining if needed?
#TODO when roles added to someone, record in database

#reaction roles
@client.event 
async def on_raw_reaction_add(arg):
    guild = await client.fetch_guild(arg.guild_id)
    channels = await guild.fetch_channels()
    channel = None
    section_role_emotes = ('0️⃣', '1️⃣', '2️⃣', '3️⃣', '4️⃣', '5️⃣', '6️⃣', '7️⃣', '8️⃣', '9️⃣')
    emoji = -1
    for i,r in enumerate(section_role_emotes): 
        if str(arg.emoji) == r: emoji = i
    if emoji == -1: return
    for c in channels:
        if c.id == arg.channel_id:
            channel = c 
            break 
    if channel is None: return 
    if channel.name != 'roles': return
    msg = await channel.fetch_message(arg.message_id)
    cont = msg.content
    if not cont.startswith('0️⃣'): return 
    role_names = []
    while True:
        ind = cont.find('\n')
        if (ind == -1): role_names.append(cont[7:])
        else: role_names.append(cont[7:ind])
        cont = cont[ind+1:]
        if cont[0] != '\n': break
        cont = cont[1:]
    role_name = role_names[emoji]

    member = await guild.fetch_member(arg.user_id)

    roles = await guild.fetch_roles()
    for r in roles:
        if r.name == role_name:
           await member.add_roles(r)
@client.event 
async def on_raw_reaction_remove(arg):
    guild = await client.fetch_guild(arg.guild_id)
    channels = await guild.fetch_channels()
    channel = None
    section_role_emotes = ('0️⃣', '1️⃣', '2️⃣', '3️⃣', '4️⃣', '5️⃣', '6️⃣', '7️⃣', '8️⃣', '9️⃣')
    emoji = -1
    for i,r in enumerate(section_role_emotes): 
        if str(arg.emoji) == r: emoji = i
    if emoji == -1: return
    for c in channels:
        if c.id == arg.channel_id:
            channel = c 
            break 
    if channel is None: return 
    if channel.name != 'roles': return
    msg = await channel.fetch_message(arg.message_id)
    cont = msg.content
    if not cont.startswith('0️⃣'): return 
    role_names = []
    while True:
        ind = cont.find('\n')
        if (ind == -1): role_names.append(cont[7:])
        else: role_names.append(cont[7:ind])
        cont = cont[ind+1:]
        if cont[0] != '\n': break
        cont = cont[1:]
    role_name = role_names[emoji]

    member = await guild.fetch_member(arg.user_id)

    roles = await guild.fetch_roles()
    for r in roles:
        if r.name == role_name:
           await member.remove_roles(r)


client.run(key)