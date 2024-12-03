import discord
from discord.ext import commands
from captcha.image import ImageCaptcha
import random
import string
import os

# 봇 설정
intents = discord.Intents.default()
intents.messages = True
intents.guilds = True
intents.members = True
intents.message_content = True  # 메시지 내용 읽기 권한을 활성화

bot = commands.Bot(command_prefix="!", intents=intents)

# CAPTCHA 코드 저장용
captcha_codes = {}

# 봇 준비 완료 이벤트
@bot.event
async def on_ready():
    print(f"봇이 준비되었습니다: {bot.user}")

# CAPTCHA 생성 함수 (숫자만 포함)
def generate_captcha():
    image = ImageCaptcha(width=280, height=90)  # 이미지 크기 조정
    code = ''.join(random.choices(string.digits, k=6))  # 숫자만 6자리 생성
    image_path = f"{code}.png"
    image.write(code, image_path)  # 이미지를 파일로 저장
    return code, image_path

# 인증 명령어
@bot.command()
async def 인증(ctx):
    code, image_path = generate_captcha()
    captcha_codes[ctx.author.id] = code  # 사용자의 ID와 CAPTCHA 코드 매핑

    # CAPTCHA 이미지를 디스코드에 전송
    await ctx.send(f"{ctx.author.mention}, 아래 CAPTCHA를 입력하세요:", file=discord.File(image_path))

    # 이미지 파일 삭제 (디스크 공간 절약)
    os.remove(image_path)

# CAPTCHA 응답 처리
@bot.command()
async def 확인(ctx, 입력값: str):
    if ctx.author.id not in captcha_codes:
        await ctx.send(f"{ctx.author.mention}, 먼저 `!인증` 명령어를 사용하세요.")
        return

    # CAPTCHA 코드 확인 (공백 제거 및 비교)
    if captcha_codes[ctx.author.id].strip() == 입력값.strip():
        role_name = "길드원"  # 부여할 역할 이름
        role = discord.utils.get(ctx.guild.roles, name=role_name)
        if role:
            await ctx.author.add_roles(role)
            embed = discord.Embed(
                title="🎉 인증 성공 🎉",
                description=f"{ctx.author.mention}님, 인증에 성공했습니다! 이제 `길드원` 역할이 부여되었습니다.",
                color=discord.Color.green()
            )
            await ctx.send(embed=embed)
        else:
            await ctx.send("역할을 찾을 수 없습니다. 관리자에게 문의하세요.")
        
        del captcha_codes[ctx.author.id]  # 인증 완료 후 삭제
    else:
        await ctx.send(f"{ctx.author.mention}, CAPTCHA가 일치하지 않습니다. 다시 시도하세요.")
access_token = os.environ ["BOT_TOKEN"]
# 봇 실행 (토큰 입력)
bot.run(access_token)  # 실제 봇 토큰을 입력하세요
