class MeneameEntry:
    def __init__(self, news_id, title, content, full_story_link, meneos, clicks, karma, positive_votes, anonymous_votes, negative_votes,
                 category, comments, published_date, user, source, source_link, provincia, comunidad, scraped_date):
        self.news_id = news_id
        self.title = title
        self.content = content
        self.full_story_link = full_story_link
        self.meneos = meneos
        self.clicks = clicks
        self.karma = karma
        self.positive_votes = positive_votes
        self.anonymous_votes = anonymous_votes
        self.negative_votes = negative_votes
        self.category = category
        self.comments = comments
        self.published_date = published_date
        self.user = user
        self.source = source
        self.source_link = source_link
        self.provincia = provincia
        self.comunidad = comunidad
        self.scraped_date = scraped_date

    def to_dict(self):
        return self.__dict__