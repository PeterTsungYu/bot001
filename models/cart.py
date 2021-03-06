# pip3 install cachelib

# import libarys
from cachelib import SimpleCache
from linebot.models import *

# import custom packages
from database import db_session
from models.products import Products


cache = SimpleCache(threshold=500, default_timeout=0) # it is like a dict {id:<dict>}
#print(dir(cache))
#print(cache.get_many())

class Cart(object):
    def __init__(self, user_id):
        self.cache = cache
        self.user_id = user_id

    def bucket(self):
        return cache.get(key=self.user_id) # return a dict or None

    def add(self, datetime, product, num):
        bucket = cache.get(key=self.user_id)
        #print(bucket)
        if bucket == None:
            cache.add(key=self.user_id, value={datetime:{product:int(num)}}) # equal to cache.set()
        elif datetime in bucket.keys():
            bucket[datetime].update({product:int(num)}) # dict.update(), could update a pair or add a new pair
            cache.set(key=self.user_id, value=bucket) # set, like updating
        else:
            bucket.update({datetime:{product:int(num)}}) # dict.update(), could update a pair or add a new pair
            cache.set(key=self.user_id, value=bucket) # set, like updating

    def reset(self):
        cache.set(key=self.user_id, value={})

    def reserve(self):
        bubbles = []
        print(self.bucket())

        for datetime, value in self.bucket().items():
            reserve_box_comp = []
            for product_name, num in value.items():
                product = db_session.query(Products).filter(Products.name.ilike(product_name)).first()

                reserve_box_comp.append(BoxComponent(
                        layout='horizontal',
                        spacing='sm',
                        contents=[
                            TextComponent(text=f"{product.name}", size='sm', color='#555555', flex=0, align='start'),
                            TextComponent(text=f"{num}", size='sm', color='#111111', align='end')
                        ]
                    )
                )
                
            bubble = BubbleContainer(
                direction='ltr',
                body=BoxComponent(
                    layout='vertical',
                    spacing='sm',
                    contents=[
                        TextComponent(
                            text=f"Reserving at {datetime}",
                            weight='bold',
                            size='xl',
                            wrap=True,
                            contents=[]
                        ),
                        SeparatorComponent(),
                        BoxComponent(
                            layout='vertical',
                            margin='xxl',
                            spacing='sm',
                            contents=reserve_box_comp
                        )
                    ]
                ),
                footer=BoxComponent(
                    layout='vertical',
                    spacing='sm',
                    contents=[
                        ButtonComponent(
                            style='primary',
                            action=PostbackAction(
                                label="Add/Revise",
                                text="Processing...Add/Revise",
                                data=f"PostbackAction:cart_datetime={datetime}"
                            )
                        ),
                        ButtonComponent(
                            action=MessageAction(
                                label="That's it", 
                                text="that's it"
                            )
                        )
                    ]
                )
            )
            bubbles.append(bubble)
        
        return FlexSendMessage(alt_text='IE125 reserve carousel', contents=CarouselContainer(contents=bubbles))

    def display(self):
        total = 0
        product_box_comp = []

        for datetime, value in self.bucket().items():
            #print(datetime, value)
            product_box_comp.append(BoxComponent(
                    layout='vertical',
                    contents=[TextComponent(text=f"{datetime}",
                                        size='sm', color='#555555', flex=0, weight="bold", align="end"),
                            SeparatorComponent(margin='sm')
                                ]
                )
                )
            for product_name, num in value.items():
                product = db_session.query(Products).filter(Products.name.ilike(product_name)).first()
                amount = product.price * int(num)
                total += amount

                product_box_comp.append(BoxComponent(
                    layout='horizontal',
                    contents=[
                        TextComponent(text=f"{num} x {product_name}",
                                        size='sm', color='#555555', flex=0),
                        TextComponent(text=f"NT$ {amount}",
                                        size='sm', color='#111111', align='end')
                    ]
                )
                )
        bubble = BubbleContainer(
            direction='ltr',
            body=BoxComponent(
                layout='vertical',
                contents=[
                    TextComponent(text=f"Here is your order:",
                                        size='md', wrap=True),
                    SeparatorComponent(margin='xxl'),
                    BoxComponent(
                        layout='vertical',
                        margin='xxl',
                        spacing='sm',
                        contents=product_box_comp
                    ),
                    SeparatorComponent(margin='xxl'),
                    BoxComponent(
                        layout='vertical',
                        margin='xxl',
                        spacing='sm',
                        contents=[
                            BoxComponent(
                                layout='horizontal',
                                contents=[
                                    TextComponent(text='Total',
                                                    size='sm', color='#555555', flex=0),
                                    TextComponent(text=f'NT$ {total}',
                                                    size='sm', color='#111111', align='end')
                                ]
                            )
                        ]
                    )
                ]
            ),
            footer=BoxComponent(
                layout='vertical',
                spacing='md',
                contents=[
                    ButtonComponent(
                        style='primary',
                        color='#1DB446',
                        action=PostbackAction(label='Checkout',
                                                display_text='checkout',
                                                data='action=checkout')
                    ),
                    BoxComponent(
                        layout='horizontal',
                        spacing='md',
                        contents=[
                            ButtonComponent(
                                style='primary',
                                color='#aaaaaa',
                                action=MessageAction(label='Empty Cart',
                                                        text='empty cart')
                            ),
                            ButtonComponent(
                                style='primary',
                                color='#aaaaaa',
                                flex=2,
                                action=MessageAction(label='Add',
                                                        text='add')
                            )
                        ]
                    )
                ]
            )
        ) 

        return FlexSendMessage(alt_text='Cart', contents=bubble)