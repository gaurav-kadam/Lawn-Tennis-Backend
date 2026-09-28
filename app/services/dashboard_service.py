from app.repositories.tournament_repo import TournamentRepository
from app.repositories.player_repo import PlayerRepository
from app.repositories.official_repo import OfficialRepository
from app.repositories.match_repo import MatchRepository


def get_dashboard_summary(db):
    summary = {}
    for name, count in (
        ("tournament", TournamentRepository.count_tournaments),
        ("player", PlayerRepository.count_players),
        ("official", OfficialRepository.count_officials),
        ("match", MatchRepository.count_matches),
    ):
        summary[name] = {
            "active": count(db, is_active=True),
            "inactive": count(db, is_active=False),
            "all": count(db),
        }
    return summary
