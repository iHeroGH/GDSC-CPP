from discord.ext import commands, vbu
import discord


class Welcomer(vbu.Cog):

    bot: discord.Client

    QUESTIONS = {
        "What is your name?": 'input',
        "What are your pronouns?": ('he/him', 'she/her', 'they/them'),
        "What role are you applying for?": ('General', 'Associate', 'Professional'),
        "Are you already a member?": ('Yes', 'No')
    }

    @commands.Cog.listener()
    async def on_member_join(self, member: discord.Member):
        await self.welcome_member(member)

    @commands.Cog.listener("on_component_interaction")
    async def initial_apply(self, interaction: discord.ComponentInteraction):
        """
        Deal with the application process when someone presses the apply button
        """

        if interaction.custom_id != "WELCOMER APPLY":
            return

        await self.begin_application(interaction)
    
    async def begin_application(self, interaction: discord.ComponentInteraction):
        options_picked = []
        for question, options in self.QUESTIONS.items():
            components, is_modal = Welcomer.get_application_components(question, options)
            embed = self.get_application_embed(question)

            if not is_modal:
                await interaction.response.send_message(embed=embed, components=components)
                interaction = await self.bot.wait_for("interaction", timeout=60)
                options_picked.append(interaction.component.label)
            else:
                await interaction.response.send_modal(modal=components)
                interaction = await self.bot.wait_for("modal_submit", timeout=60)
                options_picked.append(interaction.components[0].components[0].value)
        
        await interaction.response.defer_update()
        await interaction.channel.send(options_picked)


    @commands.command()
    @commands.is_owner()
    async def force_welcome(self, ctx: vbu.Context, member: discord.Member = None):
        """
        Forcefully sends the welcome message to a member
        """
        member = member or ctx.author
        await self.welcome_member(member)
        await ctx.okay()

    async def welcome_member(self, member: discord.Member):
        await self.send_welcome_message(member)
    
    async def send_welcome_message(self, member: discord.Member):
        welcome_embed = vbu.Embed(
            title = "Welcome to GDSC CPP!", 
            description = "Please press the 'Apply' button below to get started!\n",
            use_random_colour=True
            )

        apply_button = discord.ui.MessageComponents(
            discord.ui.ActionRow(
                discord.ui.Button(
                    label='Apply',
                    style=discord.ButtonStyle.green,
                    custom_id='WELCOMER APPLY'
                )
            )
        )

        await member.send(embed=welcome_embed, components=apply_button)
    
    @staticmethod
    def get_application_embed(title: str = None):
        embed = vbu.Embed(use_random_colour=True)
        if not title:
            embed.title = "GDSC CPP Application"
        else:
            embed.title = title
            embed.set_footer(text="GDSC CPP Application")
        
        return embed

    @staticmethod
    def get_application_components(question: str, options: tuple | str):
        
        if options == 'input':
            modal = discord.ui.Modal(
                title='GDSC CPP Application',
                components=[
                    discord.ui.ActionRow(
                        discord.ui.InputText(
                            label=question,
                            placeholder='Enter Here!',
                            min_length=1
                        )
                    )
                ]
            )
            return modal, True

        interactables = []
        for option in options:
            interactable = discord.ui.Button(
                label=option,
                style=discord.ButtonStyle.blurple,
                custom_id=f"WELCOMER APPLY BUTTON {option}"
            )

            interactables.append(interactable)

        componenets = discord.ui.MessageComponents(
            discord.ui.ActionRow(
                *interactables
            )
        )

        return componenets, False



def setup(bot: vbu.Bot):
    x = Welcomer(bot)
    bot.add_cog(x)