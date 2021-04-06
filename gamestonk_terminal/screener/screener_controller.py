"""Screener Controller Module"""
__docformat__ = "numpy"

import os
import argparse
from typing import List
from gamestonk_terminal import feature_flags as gtff
from gamestonk_terminal.helper_funcs import get_flair
from gamestonk_terminal.menu import session
from prompt_toolkit.completion import NestedCompleter
from gamestonk_terminal.helper_funcs import (
    parse_known_args_and_warn,
)
from gamestonk_terminal.screener import finviz_view
from gamestonk_terminal.screener import yahoo_finance_view


class ScreenerController:
    """Screener Controller class"""

    # Command choices
    CHOICES = [
        "help",
        "q",
        "quit",
        "view",
        "set",
        "historical",
        "overview",
        "valuation",
        "financial",
        "ownership",
        "performance",
        "technical",
        "signals",
    ]

    def __init__(self):
        """Constructor"""
        self.preset = "template"
        self.scr_parser = argparse.ArgumentParser(add_help=False, prog="scr")
        self.scr_parser.add_argument(
            "cmd",
            choices=self.CHOICES,
        )

    @staticmethod
    def print_help(self):
        """Print help"""

        print("\nScreener:")
        print("   help          show this screener menu again")
        print("   q             quit this menu, and shows back to main menu")
        print("   quit          quit to abandon program")
        print("")
        print("   view          view available presets")
        print("   set           set one of the available presets")
        print("")
        print(f"PRESET: {self.preset}")
        print("")
        print("   historical     view historical price of stocks that meet preset")
        print("   overview       overview information")
        print("   valuation      valuation information")
        print("   financial      financial information")
        print("   ownership      ownership information")
        print("   performance    performance information")
        print("   technical      technical information")
        print("")
        print("   signals        view filter signals (e.g. -s top_gainers)")
        print("")

    @staticmethod
    def view_available_presets(other_args: List[str]):
        """ View available presets. """
        parser = argparse.ArgumentParser(
            add_help=False,
            prog="view",
            description="""View available presets under presets folder.""",
        )

        try:
            ns_parser = parse_known_args_and_warn(parser, other_args)
            if not ns_parser:
                return

            presets = [
                preset.split(".")[0]
                for preset in os.listdir("gamestonk_terminal/screener/presets")
                if preset[-4:] == ".ini"
            ]

            for preset in presets:
                with open(
                    "gamestonk_terminal/screener/presets/" + preset + ".ini",
                    encoding="utf8",
                ) as f:
                    description = ""
                    for line in f:
                        if "[General]" == line.strip():
                            break
                        description += line.strip()
                print(f"\nPRESET: {preset}")
                print(description.split("Description: ")[1].replace("#", ""))

        except Exception as e:
            print(e)

        print("")
        return

    @staticmethod
    def set_preset(self, other_args: List[str]):
        """ Set preset """
        parser = argparse.ArgumentParser(
            add_help=False,
            prog="set",
            description="""Set preset from under presets folder.""",
        )
        parser.add_argument(
            "-p",
            "--preset",
            action="store",
            dest="preset",
            type=str,
            default="template",
            help="Filter presets",
            choices=[
                preset.split(".")[0]
                for preset in os.listdir("gamestonk_terminal/screener/presets")
                if preset[-4:] == ".ini"
            ],
        )

        try:
            if other_args:
                if "-" not in other_args[0]:
                    other_args.insert(0, "-p")

            ns_parser = parse_known_args_and_warn(parser, other_args)
            if not ns_parser:
                return

            self.preset = ns_parser.preset

        except Exception as e:
            print(e)

        print("")
        return

    def switch(self, an_input: str):
        """Process and dispatch input

        Returns
        -------
        True, False or None
            False - quit the menu
            True - quit the program
            None - continue in the menu
        """
        (known_args, other_args) = self.scr_parser.parse_known_args(an_input.split())

        return getattr(
            self, "call_" + known_args.cmd, lambda: "Command not recognized!"
        )(other_args)

    def call_help(self, _):
        """Process Help command"""
        self.print_help(self)

    def call_q(self, _):
        """Process Q command - quit the menu"""
        return False

    def call_quit(self, _):
        """Process Quit command - quit the program"""
        return True

    def call_view(self, other_args: List[str]):
        """Process view command"""
        self.view_available_presets(other_args)

    def call_set(self, other_args: List[str]):
        """Process overview command"""
        self.set_preset(self, other_args)

    def call_historical(self, other_args: List[str]):
        """Process historical command"""
        yahoo_finance_view.historical(other_args, self.preset)

    def call_overview(self, other_args: List[str]):
        """Process overview command"""
        finviz_view.screener(other_args, self.preset, "overview")

    def call_valuation(self, other_args: List[str]):
        """Process valuation command"""
        finviz_view.screener(other_args, self.preset, "valuation")

    def call_financial(self, other_args: List[str]):
        """Process financial command"""
        finviz_view.screener(other_args, self.preset, "financial")

    def call_ownership(self, other_args: List[str]):
        """Process ownership command"""
        finviz_view.screener(other_args, self.preset, "ownership")

    def call_performance(self, other_args: List[str]):
        """Process performance command"""
        finviz_view.screener(other_args, self.preset, "performance")

    def call_technical(self, other_args: List[str]):
        """Process technical command"""
        finviz_view.screener(other_args, self.preset, "technical")

    def call_signals(self, other_args: List[str]):
        """Process signals command"""
        finviz_view.view_signals(other_args)


def menu():
    """Screener Menu"""

    scr_controller = ScreenerController()
    scr_controller.call_help(None)

    while True:
        # Get input command from user
        if session and gtff.USE_PROMPT_TOOLKIT:
            completer = NestedCompleter.from_nested_dict(
                {c: None for c in scr_controller.CHOICES}
            )
            an_input = session.prompt(
                f"{get_flair()} (scr)> ",
                completer=completer,
            )
        else:
            an_input = input(f"{get_flair()} (scr)> ")

        try:
            process_input = scr_controller.switch(an_input)

            if process_input is not None:
                return process_input

        except SystemExit:
            print("The command selected doesn't exist\n")
            continue
