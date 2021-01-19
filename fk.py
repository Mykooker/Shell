from lxml import etree
import requests
from telegram.ext import Updater, CommandHandler
import logging
import re

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

# 商品列表,可以放置多个链接
url_list = ['https://paofu.fr/product/29.html',
            'https://paofu.fr/product/30.html',
             'https://paofu.fr/product/25.html',
            'https://paofu.fr/product/19.html']
# bot_token
bot_token = '1509791380:AAFI8Na_zha_9b5HvZgFiNvACqBhD0zgKIo'
# 监控间隔,单位秒
send_time = 60


def get_product_info(url):
    headers = {
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                      "AppleWebKit/537.36 (KHTML, like Gecko) "
                      "Chrome/83.0.4103.97 Safari/537.36"}
    response = requests.get(url, headers = headers)
    response.encoding = 'utf-8'
    selector = etree.HTML(response.text)
    name = selector.xpath('//*[@id="zlkbbody"]/div[3]/div/div/fieldset/div/div[2]/div/form/p[1]/span[2]/text()')[0]
    price = selector.xpath('//*[@id="zlkbbody"]/div[3]/div/div/fieldset/div/div[2]/div/form/p[2]/span[2]/text()')[0]
    status_tamp = selector.xpath('//*[@id="zlkbbody"]/div[3]/div/div/fieldset/div/div[2]/div/form/div[1]/div[2]/text()')[0]
    status = status_tamp
    text = f'{name, price, status}'
    logger.info(text)
    return text


def get_status(context):
    job = context.job
    chat_id = job.context.chat_id
    for url in url_list:
        text = get_product_info(url)
        if re.search(r'库存:\d+', text):
            context.bot.send_message(chat_id=chat_id, text=text, disable_notification=False)


def start(update, context):
    if 'job' in context.chat_data:
        old_job = context.chat_data['job']
        old_job.schedule_removal()
    send_message = update.message.reply_text('已经开始监控\n\n'
                                             '发送/stop 可以停止监控')
    new_job = context.job_queue.run_repeating(get_status, send_time, context=send_message)
    context.chat_data['job'] = new_job


# 停止获取任务状态
def stop(update, context):
    if 'job' not in context.chat_data:
        update.message.reply_text('当前无监控')
        return

    job = context.chat_data['job']
    job.schedule_removal()
    del context.chat_data['job']
    update.message.reply_text(f'已经停止监控')


if __name__ == '__main__':
    updater = Updater(token=bot_token, use_context=True)
    updater.dispatcher.add_handler(CommandHandler("start", start,
                                                  pass_args=True,
                                                  pass_job_queue=True,
                                                  pass_chat_data=True))
    updater.dispatcher.add_handler(CommandHandler("stop", stop, pass_chat_data=True))
    updater.start_polling()
    updater.idle()
