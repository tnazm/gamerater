# GameJourneys

Keep track of the games you're playing, and write your thoughts on them. Users can use it to write their thoughts on the games they've played, or share a list of their reviews on games with friends. Users can add games to several lists: a backlog of unplayed games, games they're currently playing through, or games they've finished.

## Distinctiveness and Complexity

An API is accessed to fill out data about specific games when viewing them on the website, which isn't done in any other project. The concept of a video game journaling website and saving games in lists is distinct from other projects as well. A through relationship model is also used between the Games and Users. This model stores extra data that a ForeignKey can't: which list a user has placed it on and a written journal entry. Javascript and React is used to update the database from the frontend without refreshing the page. The webpage is mobile responsive; the navbar shrinks into a dropdown and content is rearranged to make it easier to read when scrolling.

## Files Created

- capstone
  - gamerater
    - igdb_utils.py
      Stores functions which interface and grab data from the IGDB api, and stores game data in the Django model database.
    - models.py
      Defines the models for storing information through a database. Models are used to cache data about games and a through model relationship to store user's journal entries and lists of games.
    - views.py
      Stores all backend functions that return data to the browser to be viewed.
    - urls.py
      Directs URLs to the appropriate view functions.
    - templates
      - gamerater
        - add_list_form.html
          When included in other pages, it renders the form to change which list you've put a game on. You can add a game onto a backlog of untouched games, games you're currently playing through, or games you've finished.
        - game.html
          Lists information (like genre and a Metacritic rating) about a specific game, and lets you edit your journal entry and which list it's on.
        - game_item.html
          Single result of video game included in results page.
        - game_item.html
          Single result of video game on a user's page, which includes their journal entry if shown.
        - game_list.html
          Shows one of a specific user's video game lists with pagination.
        - index.html
          Main home page. Includes a small explanation of the website's features and shows 10 random video games with a rating of 85 or higher.
        - layout.html
          Base template with navbar and common reused Javascript for the change list form.
        - login.html
          Login page.
        - register.html
          Register as new user.
        - results.html
          Shows results from a search query made by user in the navbar.
        - user.html
          User's profile page. Shows their lists of games and their journal entries. Can be viewed by anyone.
        - users_dir.html
          List of all users registered with website.
    - static
      - gamerater
        - styles.css
          CSS stylesheet to make website look presentable.

## How to Run

Required modules are listed in requirements.txt.

For the IGDB api calls to work, you need to make a Twitch dev account to generate a client ID and secret, and then set those as environment variables before starting the server.

1. [Make a Twitch account](https://dev.twitch.tv/login)
2. [Enable Two Factor Authentication](https://www.twitch.tv/settings/security)
3. [Register a developer application](https://dev.twitch.tv/console/apps/create) (needed to generate id).
4. [Manage your newly created application](https://dev.twitch.tv/console/apps)
5. Generate a Client Secret by pressing [New Secret]
6. Take note of the Client ID and Client Secret
7. Fill in the strings in the following code block with the client ID and secret, and run the commands in the terminal before starting the application.

```sh
export IGDB_CLIENT_ID=""
export IGDB_CLIENT_SECRET=""
python manage.py runserver
```
