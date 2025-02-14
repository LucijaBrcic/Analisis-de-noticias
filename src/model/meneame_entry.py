from dataclasses import dataclass, asdict

# Clase para representar una "entrada" en meneame
@dataclass
class MeneameEntry:
    id: int
    title: str
    meneos: int
    clicks: int
    karma: int
    positive_votes: int
    anonymous_votes: int
    negative_votes: int
    category: str
    comments: int
    published_timestamp: int
    scraped_timestamp: int

    def to_dict(self):
        return asdict(self)
