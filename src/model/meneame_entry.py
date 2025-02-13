# Clase para representar una "entrada" en meneame
class MeneameEntry:
    def __init__(self,
                 id: int,
                 title: str,
                 meneos: int,
                 clicks: int,
                 karma: int,
                 positive_votes: int,
                 anonymous_votes: int,
                 negative_votes: int,
                 category: str,
                 comments: int,
                 published_timestamp: int,
                 scraped_timestamp: int):

        self.id = id
        self.title = title
        self.meneos = meneos
        self.clicks = clicks
        self.karma = karma
        self.positive_votes = positive_votes
        self.anonymous_votes = anonymous_votes
        self.negative_votes = negative_votes
        self.category = category
        self.comments = comments
        self.published_timestamp = published_timestamp
        self.scraped_timestamp = scraped_timestamp

    def __str__(self):
        return f"{self.id} # {self.title} # {self.published_timestamp}"

    def __repr__(self):
        return f"{self.id} # {self.title} # {self.published_timestamp}"

