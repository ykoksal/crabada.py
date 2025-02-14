from __future__ import annotations
from typing import List, Tuple
from eth_typing import Address
from web3.types import Wei
from src.common.config import users
from src.common.exceptions import UserException
from src.common.types import ConfigTeam, ConfigUser, TeamTask, Tus
from src.helpers.general import findInList, firstOrNone
from src.libs.CrabadaWeb2Client.types import Game, Team, TeamStatus
from src.models.Model import Model

class User(Model):
    """
    A user with his/her configuration, uniquely identified by
    its wallet address
    """

    config: ConfigUser = None

    def __init__(self, userAddress: Address):
        self.config = User.getUserConfig(userAddress)
        if not self.config:
            raise UserException("User address not registered: {userAddress}")

    def getTeamConfig(self, teamId: int) -> ConfigTeam:
        """
        Return the configuration of the team with the given team ID;
        if the team does not belong to the current user, return None.
        """
        return findInList(self.config['teams'], 'id', teamId)  # type: ignore

    def getTeams(self) -> List[ConfigTeam]:
        """
        Return the user teams as specified in the configuration
        """
        return self.config['teams']

    def getTeamConfigFromMine(self, mine: Game) -> Tuple[ConfigTeam, TeamStatus]:
        """
        Given a game, return the team mining or looting it; if the current user
        has no teams in the game, return None.

        To check whether the returned team is mining or looting, you can use the
        second returned value which is either 'loot' or 'mine'.

        TODO: Here we assume that the user cannot have both teams in the same
        game. Verify this is ok.
        """

        miningTeamId = mine['team_id']
        miningTeamConfig = self.getTeamConfig(miningTeamId)
        if miningTeamConfig:
            return (miningTeamConfig, 'MINING')

        lootingTeamId = mine['attack_team_id']
        lootingTeamConfig = self.getTeamConfig(lootingTeamId)
        if lootingTeamConfig:
            return (lootingTeamConfig, 'LOOTING')
        
        return (None, None)

    def isTooExpensiveToBorrowTus(self, price: Tus) -> bool:
        """
        Return whether a crab costs too much to borrow for the user
        """
        return price > self.config['maxPriceToReinforceInTus']

    def isTooExpensiveToBorrowTusWei(self, price: Wei) -> bool:
        """
        Return whether a crab costs too much to borrow for the user
        """
        return price > self.config['maxPriceToReinforceInTusWei']

    @staticmethod
    def isRegistered(userAddress: Address) -> bool:
        """Return true if the given user is in the list
        of registered users"""
        return True if User.getUserConfig(userAddress) else False

    @staticmethod
    def getUserConfig(userAddress: Address) -> ConfigUser:
        """Return a user configuration given its address;
        returns None if no user with that address is found"""
        return firstOrNone([ u for u in users if u['address'] == userAddress ])

    @staticmethod
    def create(userAddress: Address) -> User:
        """
        User factory
        """
        return User(userAddress)