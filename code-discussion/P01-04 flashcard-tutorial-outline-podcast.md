# BUILDING A FLASHCARD API FROM ZERO — OUTLINE STUDY PODCAST
## FastAPI, Supabase & Multi-User Architecture — Companion Audio Guide

---

Welcome. You should have the printed outline in front of you. We'll be working through it together. Not reading it aloud — actually working through it. When there's a table or a diagram worth looking at, we'll point you to it. When we're just talking through ideas, sit back and listen. Let's begin. Section I.

---

---

## SECTION I — WHY FASTAPI AND WHAT PROBLEM DOES IT SOLVE

---

❒ So we're building a flashcard API. Before we touch any code — why do we even need an API? What problem are we actually solving?

Here's the situation. You're a Python developer. You've written a script that reads flashcard data from a JSON file. It processes it beautifully. Prints it to the terminal. Works great. You're happy. Then someone says: "I want to use your flashcards on my phone." And you hit a wall. Your script runs, does its thing, and exits. There's no door. No way for an outside device to reach in and say "give me those flashcards." The script is a closed room.

❒ Okay, but couldn't we just put the JSON file on a web server? Then anyone could download it.

Good thought, but it doesn't work. A static file on a web server solves one problem — retrieval. Anyone can grab the file. Great. But now try to create a new flashcard. Try to edit one. Try to delete one. You can't. The file is inert. It just hands you the same content every time. Look at subsection A in your outline — it lays out three points. The limitation of scripts. The insufficiency of static files. And then the solution.

❒ Which is an API.

Right. An API — Application Programming Interface — is a program that stays alive. It sits on a server, permanently listening. A request comes in. The API figures out what it wants. Are you reading data? Creating something? Updating? Deleting? Then it does the work. Think of a receptionist at a front desk. The filing cabinets behind them are your database. Without the receptionist, the cabinets exist but nobody from outside can interact with them. The API is that receptionist. Always present. Always ready.

❒ Alright, so an API listens for requests. But how does it know what I'm asking for? If I say "flashcards" — do I want all of them? Just one? Do I want to create a new one?

Two things work together. First, the endpoint. That's a specific URL, like localhost 8000 slash cardfolders. Different URLs point to different resources. Second, the HTTP method. That's the verb attached to your request. And this is where it gets elegant. Flip to subsection B in your outline. There's a table mapping HTTP methods to CRUD operations.

❒ I see it. GET, POST, PUT, DELETE.

Exactly. GET means read. Just retrieve data, don't touch anything. POST means create. I'm sending you new data, store it. PUT means update. Here's a modified version of something that already exists. DELETE means remove it. Four verbs, four operations. Create, Read, Update, Delete. The acronym CRUD. This is the foundation of virtually every data-driven application you'll ever build. Your email, your social media, your banking app. Under the hood, it's all CRUD operations on a database, exposed through an API.

❒ That's a clean mapping. So now the question is — what tool do we use to build this API? Python has options, right?

It does. Subsection C in your outline lists three major Python frameworks. Let me explain why two of them lose.

Flask is the oldest. It's a micro-framework. Gives you the bare minimum. You build everything else yourself. Need data validation? Write it by hand. Need documentation? Install a plugin and configure it. It's like getting an empty room and being told to build your own furniture.

Django REST Framework is the opposite extreme. Built on top of Django, a full-featured web framework. Powerful, but it comes with an enormous amount of machinery. An ORM, an admin panel, a template system. For a focused API project, it's like renting a warehouse when you need a workshop.

❒ So FastAPI sits in between?

Not exactly between. It takes a fundamentally different approach. FastAPI was designed in 2018. Decades after Flask and Django. It was built to exploit modern Python features that didn't exist when those older frameworks were created. Here's what that means in practice.

First benefit. Automatic data validation. FastAPI uses a library called Pydantic. The name's a play on "pedantic." It lets you define the exact shape of data you expect. This field must be a string. This one must be an integer. This one is optional. When a request arrives that doesn't match, Pydantic rejects it instantly. Sends back a detailed error message. A 422 Unprocessable Entity response. You write zero validation code. In Flask, you'd write all of that by hand. Check every field, check its type, check if it's present. Tedious, error-prone work that FastAPI eliminates completely.

❒ So the framework guards your door for you.

Exactly. Bad data never touches your database. It's caught at the boundary.

Second benefit. Automatic interactive documentation. The moment your FastAPI server starts, it generates a fully interactive docs page at slash docs. You can see every endpoint. You can see what data each one expects. And here's the key. You can test them right in your browser. Click "Try it out." Fill in some data. Hit execute. No Postman. No curl. No external tools during development. It builds itself from your code.

❒ Wait — it generates docs from your code? How?

That's the third benefit. And it's the cleverest part. FastAPI uses Python's native type hint system for a dual purpose. When you write something like "front_text_1: str," that single annotation does two jobs at once. It tells Pydantic to validate that the value is a string. And it tells the docs generator to display it as a string field. One line of code. Two jobs done. In Flask, validation and documentation are separate systems you maintain independently.

There's also async support. FastAPI can handle many requests concurrently without blocking. We're using synchronous code in this tutorial for simplicity, but the capability is there when you need it.

❒ Okay. So we have our framework. Now we need a database. The outline mentions Supabase — why not just use a local database like SQLite?

SQLite would work. For exactly one person, on exactly one machine. It stores everything in a single file on your local disk. Fine for a personal script. But remember our original problem. External clients need to access the data. A phone in another city can't read a file on your laptop.

Supabase solves this. It gives you a hosted PostgreSQL database. That's one of the most powerful relational databases in the world. Used by Instagram, Spotify, Netflix. But Supabase wraps it in a friendly interface. You get a visual web dashboard. You can create tables, inspect data, run queries. All through your browser. And the Python client library is clean. You write things like "supabase.table('cards').select('*').execute()." Very readable. Very consistent.

And here's the kicker. When you eventually deploy your API to a production server, the Supabase connection works identically. No migration. No reconfiguration. Same code.

❒ That's three advantages. Remote accessibility. Visual dashboard. Clean Python client. Now, subsection E is the big one. It talks about four features that transform what we're building from a toy into a real platform. What are they?

This is where it gets interesting. Imagine we've built a simple flashcard API. One user. No security. No access control. It works. Now imagine two people use it. Immediately, we have problems.

Problem one. User A creates a card set called "Spanish Verbs." Can User B delete it? Of course not. But nothing in a naive system prevents it. We need ownership. Every folder, every card set must know who created it. Every write operation must check: are you the owner? If not, you're blocked.

❒ So that's feature one — ownership.

Right. Feature two is visibility. Say you've built a great card set and you want to share it publicly. Anyone can browse it. But you also have private card sets. Personal study notes you don't want others to see. Each card set needs a flag called "is_public." It defaults to false. Private unless you explicitly say otherwise.

❒ Makes sense. What about tracking changes?

That's feature three. Audit trails. If someone edits a flashcard and the text gets corrupted, you want to know when it happened and who did it. Every card modification gets stamped with a timestamp — "updated_at" — and the identity of the person who made the change — "updated_by." A permanent record.

❒ And feature four?

Feature four is copying. This is the one that really makes the platform useful. Imagine a Spanish teacher builds a beautiful 200-card set and shares it publicly. A student finds it. Loves it. But wants to personalise it. Add notes. Remove cards they already know. Tweak translations. The student can't edit the original. They're not the owner. And even if they could, their changes would affect every other student. So the API supports a deep copy. A complete, independent clone into the student's own account. Their copy, their rules. The original untouched.

❒ That's a nice set of features. Let me check the section summary in the outline. Static files can't handle CRUD. FastAPI was chosen for validation, documentation, and type hints. Supabase for remote hosting and the dashboard. And these four multi-user features. Ownership. Visibility. Audit trails. Copying. Eight sections ahead to build it all. Let's move on.

---

---

## SECTION II — ENVIRONMENT SETUP ON macOS

---

❒ Section II. Setting up the environment. Before we build anything, we need the workshop ready. The outline says there are four steps. They must happen in order. Why?

Because each step depends on the previous one. First, build the walls. That's your virtual environment. The isolation. Then bring in the tools. That's installing the packages. Then lock up the valuables. That's your credentials file and the gitignore. Then test the lights. That's your verification run. Try to install packages before the environment exists? They go into the wrong place. Skip the gitignore and push to GitHub? Your credentials are exposed. The sequence is deliberate.

❒ Step one — the project folder and virtual environment. What do we actually type?

Three commands. "mkdir flashcard-api" creates the folder. "cd flashcard-api" to go inside. "workon vintel" to activate the virtual environment. After that last one, your terminal prompt changes. You'll see "vintel" in parentheses at the beginning. That's your confirmation.

❒ Now, I know what a virtual environment is in general terms, but why does it matter here specifically?

Think about what happens without one. You install FastAPI for this project. Next month, you start a different project that needs an older version of one of FastAPI's dependencies. You install it. It overwrites what the flashcard project needs. Now your flashcard project is broken. And you didn't touch it. Dependency hell.

A virtual environment is a sealed room. We're using virtualenvwrapper. The "workon" command activates a named environment stored centrally. Typically in the ".virtualenvs" folder in your home directory. When you install libraries while inside, they go into that environment only. Not your system Python. Not any other project. Complete isolation.

❒ One thing the outline emphasises — and this catches people — is that the activation doesn't persist.

Right. Every time you open a new terminal window, you're starting fresh. No virtual environment active. You have to run workon vintel again. Every single time. Forget this and you'll be installing packages into your system Python wondering why nothing works.

❒ Step two — installing packages. One command?

One command. "pip install fastapi uvicorn supabase python-dotenv." Four packages. Let me explain what each one does, because they're not interchangeable. They do fundamentally different jobs.

❒ Let's start with fastapi itself.

FastAPI is the framework. The rule book. It gives you decorators like "@app.get" and "@app.post" that turn ordinary Python functions into API endpoints. It handles routing. Figuring out which function to call based on the URL. It handles parsing. Extracting data from the request. But here's what trips people up. FastAPI cannot listen for HTTP requests on its own. It's not a server. It's a set of rules and decorators. It needs an engine.

❒ And that engine is uvicorn?

Exactly. Uvicorn is an ASGI server. That stands for Asynchronous Server Gateway Interface. Think of ASGI as a contract. FastAPI speaks ASGI. Uvicorn speaks ASGI. So they can work together. Uvicorn is the piece that actually listens on a network port. Port 8000 by default. It receives incoming HTTP requests, hands them to FastAPI for processing, and sends the responses back. FastAPI defines what to do. Uvicorn is how requests arrive and depart. Two separate jobs. Two separate packages.

❒ What about the supabase package?

That's the official Python client for talking to your hosted database. It gives you that clean chained syntax. "supabase.table('cards').select('*').execute()." Nothing fancy. Just the bridge between your Python code and the PostgreSQL database in the cloud.

❒ And python-dotenv — what's that for?

This is about keeping secrets secret. Your Supabase URL and API key are credentials. If you hardcode them in your Python files and push to GitHub, anyone can see them. And access your database. python-dotenv reads a separate ".env" file. A simple text file with key-value pairs. It loads them as environment variables. Your code reads "os.environ['SUPABASE_URL']." The credentials never appear in source code.

❒ Which brings us to step three — setting up that dot env file. What goes in it?

Two lines. SUPABASE_URL equals your project URL. SUPABASE_KEY equals your anon public key. You find both in your Supabase dashboard. Open your project. Project Settings in the left sidebar. Click API. Both values are right there. Copy them in.

❒ And the gitignore — the outline says we need to protect certain files from version control.

The ".gitignore" file tells Git: never track these files. Never upload them to GitHub. Even by accident. We exclude the ".env" file. Your credentials. We exclude "__pycache__." That's Python's auto-generated bytecode cache. Not source code. And we exclude "venv/" in case a local virtual environment folder exists. None of these belong in your repository.

❒ Step four — verification. How do we know everything works?

Create a tiny test file called "test_setup.py." Import FastAPI. Create an app instance. Add one GET endpoint at slash that returns a JSON message. Then run "uvicorn test_setup:app --reload."

❒ What does that command format mean? test underscore setup colon app?

It's filename without extension, colon, variable name. So Uvicorn looks inside "test_setup.py" for an object called "app." The "--reload" flag is a development convenience. Uvicorn watches your files. Automatically restarts the server whenever you save a change. No manual stop-and-restart during development.

Open your browser to localhost:8000. You should see the JSON message. Then go to localhost:8000/docs. There's the Swagger documentation with one endpoint listed. Control C to stop the server. Delete the test file. It served its purpose.

❒ Now let's peek at the code for Section II. If you open the code supplement, you'll see the files we just talked about.

The ".env" file is two lines. That's it. Just your Supabase URL and your key. The ".gitignore" is two lines as well — ".env" and "__pycache__/." And "test_setup.py" is about five lines. Import FastAPI. Create an app. One decorator, "@app.get." One function that returns a dictionary. That's your first endpoint. Nothing more. You run it. You see it in your browser. Then you delete it.

The thing to notice here? You already have a working API. Five lines of Python and you have an endpoint that shows up in auto-generated documentation. That's the power of FastAPI.

❒ Section summary. Project folder created. Four packages installed. ".env" and ".gitignore" in place. Verification done. Clean starting point. Let's build our database.

---

---

## SECTION III — DATABASE DESIGN IN SUPABASE

---

❒ Section III. Database design. This is where we decide the shape of our data. Before we look at specific tables, let me ask a foundational question. Why not just one big table? Why can't I put everything in a single table? Users, folders, card sets, cards. All in one.

Good question. And I want you to really feel the pain before I give you the solution. Imagine one giant table. Every row is a card. Each row contains the card's content, plus the card set name, plus the folder name, plus the user's name and email. All in one row.

Now. The folder "Spanish Vocabulary" has 500 cards across 10 sets. The string "Spanish Vocabulary" is stored 500 times. Five hundred identical copies. Want to rename the folder? Update 500 rows. Miss one? Now you have 499 rows saying "Spanish Language" and one still saying "Spanish Vocabulary." Which one is correct? There's no authoritative source. Each row is a separate copy that can drift.

❒ That's the inconsistency problem.

And it gets worse. Delete all cards in a particular set. The set itself vanishes. It only existed as data repeated in card rows. There's no independent record of it. The user might have wanted to keep the empty set as a placeholder. Too bad. It's gone. That's a deletion anomaly.

And then there's user data. Without a separate users table, every card row repeats the user's name and email. User changes their email? Every card they ever touched needs updating.

❒ Okay, I feel the pain. What's the proper solution?

Normalisation. The idea was formalised by Edgar F. Codd in 1970. It's beautifully simple. Store each fact exactly once. Instead of writing "Spanish Vocabulary" 500 times, store it once in a cardfolders table. Give it a unique ID. Every card stores just that ID. A lightweight pointer. Need to rename? Change one row. Every reference to it automatically reflects the new name.

❒ So we split into separate tables. How many do we need?

Four. Look at the table in subsection A of your outline. You'll see them laid out with their dependencies. Users. That's identity. Who uses the system. Depends on nothing. Created first. Cardfolders. Containers for card sets. Depends on users. Cardsets. The actual collections, with ownership and visibility. Depends on both users and cardfolders. Cards. Individual flashcards with audit trails. Depends on cardsets and users.

❒ Let me trace the hierarchy. Users own folders. Folders contain card sets. Card sets contain cards. It's a strict chain.

Exactly. And that chain matters for creation order in the database — you can't reference a table that doesn't exist yet. Users first, then folders, then card sets, then cards.

❒ Now, these tables need to be connected somehow. The outline talks about foreign keys — what exactly is a foreign key?

Let's build from first principles. Every table has a primary key. A column that uniquely identifies each row. In our design, it's always the "id" column. A UUID. No two rows can have the same one.

A foreign key is a column in a different table that points to a primary key. The cardfolders table has a "user_id" column. Each value in that column is a UUID that matches an "id" in the users table. That's the link. "This folder belongs to this user." And here's the crucial part. The database enforces this. You literally cannot insert a "user_id" value that doesn't correspond to an existing user. The database rejects it.

❒ So the relationships are enforced, not just suggested. Now — what happens when you delete a parent? If I delete a user, what happens to their folders?

This is one of the most important design decisions in the whole project. The outline lays out two options at subsection C point two. Let me give you both.

Option one. CASCADE. When you delete the parent, all children are automatically deleted. The logic is simple. If the child can't meaningfully exist without the parent, destroy them together. A folder without an owner makes no sense. A card set without a folder makes no sense. A card without a card set makes no sense. Delete a user. Their folders cascade away. Delete a folder. Its card sets cascade. Delete a card set. Its cards cascade.

❒ That's clean. What's option two?

Option two. SET NULL. When you delete the referenced entity, the foreign key column is set to null. But the child survives. The logic? The reference is informational, not existential. Think about the audit trail. A card has an "updated_by" field pointing to the user who last edited it. That user's account gets deleted. Should the card be destroyed? Absolutely not. It belongs to someone else. It's perfectly valid. We just lose the information about who made that particular edit. The field becomes null. "The person who last edited this card no longer exists."

❒ Oh — so CASCADE is for existential relationships and SET NULL is for informational references. That's a clean distinction.

And it's consistent throughout the whole design. Look at the table in your outline. Four rows. User deleted? Folders cascade. Folder deleted? Card sets cascade. Card set deleted? Cards cascade. But user deleted and the "updated_by" field on cards they edited? SET NULL. The card lives on. Only the editor reference clears.

❒ Let me ask about the multi-user columns specifically. The outline has three categories in subsection D.

Right. Category one. Ownership. Both cardfolders and cardsets carry a "user_id" column pointing to the users table. Every write operation checks this column. Does the requester match the owner? If not, 403 Forbidden.

Now here's a subtle design choice. Cards don't have their own "user_id." Card ownership is inherited from the parent card set. If you own the set, you own the cards inside it. This avoids duplicating ownership data at the card level.

❒ Category two — visibility?

The cardsets table has an "is_public" boolean. Defaults to false. Private unless you explicitly flip it. And notice. This lives at the card set level. Not the folder level.

❒ Why not the folder level? That seems like it would be simpler.

Think about it. You have a folder called "Languages" with three card sets inside. "Spanish Basics." "French Verbs." And your private "Embarrassing Mistakes." If visibility is on the folder, it's all-or-nothing. Share everything or nothing. But if visibility is on the card set, you can make "Spanish Basics" public. Keep "Embarrassing Mistakes" private. No contradiction. Each set is independently controlled.

And consider this. A public card set inside a private folder. What should happen? Is it visible or not? The rules conflict. Keeping visibility on card sets avoids that ambiguity entirely.

❒ Category three — the audit columns.

On the cards table only. "updated_at" is a timestamptz. Starts as null. "updated_by" is a UUID pointing to users. Also starts null. SET NULL on delete. When a card is modified, both get stamped. A null "updated_at" clearly communicates something specific. This card has never been edited since creation. It's not "we don't know when it was edited." It's "it hasn't been."

❒ Now let's actually create these tables. The outline has a step-by-step in subsection E. First — how do we navigate the Supabase dashboard?

Log into supabase.com. Open your project. The left sidebar has a bunch of options. Authentication, Database, Storage, and more. The one you want is Table Editor. It gives you a graphical interface for creating tables without writing any SQL. Click New Table. And one important note right away. Uncheck "Enable Row Level Security." We're handling security at the API level in this tutorial. Not at the database level.

❒ Let's go table by table. The outline has detailed column tables for each one — I'm looking at them now. Table one: users.

Four columns. The "id." Type UUID. Primary key. Not null. With a default of "gen_random_uuid()." That function generates a UUID automatically for every new row. UUID stands for Universally Unique Identifier. A 128-bit number. A 36-character string. The odds of two colliding are astronomically small.

Then "username." Text. Not null. And crucially, unique. "email." Same thing. Text, not null, unique. The UNIQUE constraint means the database itself rejects duplicates. To set it in Supabase, click the gear icon on the column and check "Is Unique."

Finally, "created_at." Type timestamptz. Default of "now()." Timestamptz is PostgreSQL's timestamp type that includes timezone information. Timestamps stay consistent regardless of where the server is.

❒ Table two — cardfolders. I can see it depends on users.

Five columns. The "id." Same UUID pattern. "user_id." UUID, not null. Foreign key pointing to users.id. ON DELETE CASCADE. This is the ownership link. "name." Text, not null. "description." Text, nullable. Not every folder needs a description. "created_at." Timestamptz with "now()" default.

To create that foreign key in Supabase. Click the link icon next to "user_id." Select the users table and the id column. Set ON DELETE to CASCADE.

❒ Table three — cardsets. Two foreign keys this time.

Seven columns. "id." UUID primary key. "cardfolder_id." Points to cardfolders.id with CASCADE. "user_id." Points to users.id with CASCADE. "is_public." Boolean, not null, default false. Remember, private by default. "name." Text, not null. "description." Nullable text. "created_at." Timestamptz.

❒ And table four — cards. This is the big one. If you're following along in the outline, there's a twelve-row column table.

Let me break this into groups. First, the structural columns. "id." UUID primary key. "cardset_id." UUID, not null. Foreign key to cardsets.id with CASCADE.

Second, the content columns. Eight of them. All text. All nullable. Why nullable? Because not every card uses every field. Some might only have text. No image. Some might have audio but no image. So: "front_text_1," "front_audio_text_1," "front_audio_1," "front_image." And the same four for the back of the card.

❒ That's a lot of fields. Why separate audio text from display text?

Great question. We'll dig deep into that in Section VII. Short version. What looks good on screen sounds terrible when read aloud by a text-to-speech engine. The display text might say "El gato (the cat) [m.]" Perfectly clear visually. But a TTS engine would read the brackets and parentheses aloud. Garbled nonsense. The audio text field holds a cleaned version. Just "El gato."

❒ Makes sense. What about the audit columns?

Third group. "created_at" with a "now()" default. "updated_at." Timestamptz. Nullable. And critically, no default. It starts as null. Meaning "never edited." Not "unknown." Actively communicating: "no edits have occurred." And "updated_by." UUID. Nullable. Foreign key to users.id with ON DELETE SET NULL. Not CASCADE. Because if the editor's account is deleted, the card itself should survive. Only the reference clears.

❒ The outline mentions a complete cascade chain. Walk me through what happens when you delete a user.

It's like dominoes. Delete the user. CASCADE to their folders. CASCADE to the card sets inside those folders. CASCADE to the cards inside those sets. Everything that user owned is gone. But here's the critical nuance. Cards that the user merely edited, belonging to other users' sets? Those survive. Only the "updated_by" field on those cards is set to null. The card stays. The edit record becomes "an unknown user made this change."

❒ Section summary. Four tables in a strict hierarchy. Normalisation eliminates duplication. Foreign keys with CASCADE enforce integrity. "is_public" lives on cardsets, not folders. Audit trail on cards. SET NULL preserves cards when editors leave. Solid foundation. Now how do we organise the code?

---

---

## SECTION IV — PROJECT ARCHITECTURE

---

❒ Section IV. Project architecture. We've got four database tables. We've got a framework. Now we need to organise the actual code. Could we just write everything in one Python file?

You could. For a tiny project with two endpoints, it would be fine. But we're building 22 endpoints. Plus ownership checks. Plus visibility filters. Plus utility functions. In one file, you'd be scrolling through hundreds of lines to find anything. Change something for card sets and you might accidentally break something for users. One file does not scale.

❒ So what's the alternative?

FastAPI has a built-in solution called APIRouter. A router is essentially a mini-application that handles a subset of endpoints. One router for user operations. One for folders. One for card sets. One for cards. Each lives in its own file. Then your main application file plugs them all in with "app.include_router."

Think of it like a book. Each chapter covers one topic. That's a router file. The table of contents? That's "main.py." When you need to work on card set endpoints, you open "cardset_router.py." Nothing else is in your way.

❒ The outline has a directory tree diagram in subsection B. I'm looking at it now. Walk me through the structure.

At the top level, your flashcard-api folder. Inside it, four things directly. ".env" for credentials. ".gitignore." "main.py" as the entry point. And "database.py" for the Supabase connection.

Then three subfolders. The models folder holds Pydantic models. The data shapes for each entity. Four files. "user_models," "cardfolder_models," "cardset_models," "card_models."

The routers folder holds the endpoint logic. Same four entities. Four files. "user_router," "cardfolder_router," "cardset_router," "card_router."

And a utils folder with one file. "audio_text.py." The regex-based audio text generator.

❒ I notice each folder has an init file — double underscore init double underscore dot py. What are those?

This is a Python convention that trips people up. It seems like magic. By default, a directory in Python is just a directory. No special meaning. But the moment you place an empty file called "__init__.py" inside it, Python treats that directory as a package. You can import from it using dot notation. "from routers import cardfolder_router." Without that file, the import fails. The file can be completely empty. Just its presence changes the behaviour. Strange but essential.

❒ The outline mentions two foundational files in subsection C — database dot py and main dot py. What do they do?

"database.py" is the single connection point to Supabase. Four steps. Import os. Import load_dotenv. Import create_client from supabase. Call load_dotenv to read the ".env" file. Pull the URL and key from environment variables. Create the client. That supabase object gets imported by every router. One shared connection for the entire application.

"main.py" is the orchestrator. It creates the FastAPI instance. App equals FastAPI with a title, description, and version. Then four calls to "app.include_router." One per router. And one root endpoint at slash that returns "Flashcard API is running." A health check. You start it with "uvicorn main:app --reload."

❒ Now let's look at the code for these two foundational files.

"database.py" is about six lines of actual code. Imports at the top. Then "load_dotenv()" to read your ".env" file. Then two lines pulling the URL and key from environment variables. Then one line creating the Supabase client. That's the entire file. Every router in the project imports from this one file. One connection. Shared everywhere.

"main.py" is similarly short. Create the FastAPI app. Four lines of "include_router." One root endpoint. Done. The interesting thing to notice? This file doesn't contain a single endpoint for flashcards, folders, or users. It just plugs in the routers. All the real work lives in the router files. "main.py" is purely the orchestrator.

❒ The section summary notes something interesting. The "user_router" and "user_models" files are entirely new compared to a single-user version of this system. Everything else existed before. The multi-user dimension adds those two files. Let's move to the models.

---

---

## SECTION V — PYDANTIC MODELS

---

❒ Section V. Pydantic models. We mentioned Pydantic earlier as a validation library. Before we look at the specific models, let's understand the problem they solve. What happens without them?

Picture this. A client sends a POST request to create a flashcard. The data arrives as JSON in the request body. JSON is just text. It could contain anything. A number where a string should be. A missing required field. Extra fields that shouldn't be there. Without validation, your server blindly tries to insert whatever arrives into the database. Best case, the database throws an error. Worst case, bad data goes in silently. Corruption you don't know about.

❒ So Pydantic is the bouncer at the door.

Exactly. You define Python classes that describe the exact shape of acceptable data. FastAPI uses them to validate every incoming request before your endpoint code even runs. Data is bad? Automatic 422 response. Detailed error message listing exactly which fields failed and why. Data is good? Your code gets a clean, type-safe Python object. No guessing. No checking.

❒ The outline describes three categories of models in subsection B. Create, Update, and Response. Why three? Why not one model per entity?

Because different operations need different fields. Get this wrong and you create security holes. Let me explain each category.

Create models. What the client sends when making something new. These exclude auto-generated fields like "id" and "created_at." The database handles those. The client has no business providing them. And crucially, they exclude "user_id." Ownership comes from the request header, not the body. If "user_id" were in the create model, a malicious client could say "create this folder on behalf of User B." The server-side header assignment prevents that.

❒ So the Create model is deliberately missing fields. What about Update?

Update models define only what can be changed after creation. Every field is optional. The client might only want to change the name. Not the description. Some fields are excluded entirely. You can't change a card set's owner. That would be transferring ownership. You can't move a card set to a different folder via update. Those exclusions are deliberate constraints.

❒ And Response models?

Response models are the complete picture. Everything the client should see. They include the auto-generated "id." The "created_at" timestamp. And for cards, the audit fields. "updated_at" and "updated_by." These are the models used for what the API sends back.

❒ Let me look at the specific models in subsection C. The outline has tables for each entity. Starting with users — seems simple?

The simplest. UserCreate has just two fields. Username and email. Both required strings. UserResponse adds "id" and "created_at." No UserUpdate model. A tutorial simplification. We don't support changing usernames or emails.

❒ Card folder models?

CardfolderCreate has "name," required, and "description," optional, defaulting to None. No "user_id." That's set from the header. CardfolderResponse adds "id," "user_id," and "created_at." Now the client can see who owns the folder.

❒ Card set models — this is where it gets interesting.

Three models. CardsetCreate has "cardfolder_id." Which folder does this set go in? Plus "name," "description," and "is_public" defaulting to false. Private by default. Still no "user_id." That comes from the header.

CardsetUpdate has "name," "description," and "is_public." All optional. Look at what's excluded. No "cardfolder_id." You can't move a set to a different folder through update. No "user_id." You can't transfer ownership. Architectural constraints enforced by the model itself.

CardsetResponse shows everything. "id," "cardfolder_id," "user_id," "name," "description," "is_public," "created_at."

❒ And card models — the most complex?

CardCreate has "cardset_id." Required. A card must belong to a set. Plus eight content fields. All optional. Front text, front audio text, front audio, front image. Same four for the back.

CardUpdate has just the eight content fields. All optional. No "cardset_id." You can't move a card to a different set.

CardResponse has everything. "id," "cardset_id," all eight content fields, "created_at," and the audit fields. "updated_at" and "updated_by." Both optional. They're optional because a brand new card that's never been edited has null audit fields.

❒ The outline highlights a critical exclusion at point five. What is it?

"updated_at" and "updated_by" appear only in CardResponse. Never in CardCreate. Never in CardUpdate. The API sets them automatically during updates. No client can provide them. No one can fake their audit trail. If they appeared in the Update model, a malicious user could stamp someone else's ID. Or backdate a timestamp. The model prevents it.

❒ Now, subsection D covers how the API identifies the requesting user. The outline describes a simplified authentication using the x-user-id header. How does that work?

The client sends their user ID as an HTTP header called "x-user-id" with every request. FastAPI reads it using the Header dependency. Two syntax forms. "Header(...)" with an ellipsis. The header is required. Missing it gives a 422 error. "Header(default=None)." Optional. Value is None if missing. And there's a nice automatic conversion. Python uses underscores in variable names. HTTP headers use hyphens. You write "x_user_id" in Python. The client sends "x-user-id" as the header. FastAPI converts between them automatically.

❒ But the outline warns this isn't secure for production.

Correct. Anyone can fake the header. There's no verification that the user ID actually belongs to the person sending the request. In production, you'd use JWT tokens, OAuth, or Supabase Auth. But the ownership and visibility logic? Checking who you are. Comparing you to the resource owner. That's identical regardless of how you establish identity. We're learning the logic. Not the authentication infrastructure.

❒ Now let's look at the model code itself.

If you open the code supplement, you'll see four model files. The simplest is "user_models.py." Two classes. UserCreate and UserResponse. Each is about four lines. That's it. Just class definitions with typed fields.

"cardfolder_models.py" is similarly compact. Two classes again. Notice the "Optional[str] = None" pattern on description. That's how you say "this field is optional and defaults to None."

"cardset_models.py" is where it gets interesting. Three classes. This is the first entity with all three model types. Create, Update, and Response. Look at the Update model. Every field is Optional. That's what enables partial updates. The client only sends what they want to change.

"card_models.py" is the largest. Eight content fields in both Create and Update. But notice what's only in Response. "updated_at" and "updated_by." The audit trail fields. The server controls those. Never the client.

The thing to notice across all four files? How small they are. Each file is maybe 20 to 30 lines. But those few lines of type definitions give you automatic validation, automatic documentation, and security constraints. Pydantic does a lot of heavy lifting from very little code.

❒ Section summary. Pydantic models in three categories. "user_id" never in Create models. "is_public" defaults to false. Audit fields only in Response models. Simplified auth via the header. Let's build the actual endpoints.

---

---

## SECTION VI — BUILDING EVERY ENDPOINT

---

❒ Section VI. This is the main event. We're building every endpoint. How many are we talking about?

Twenty-one across four routers. Plus one more copy endpoint in Section VIII for a total of twenty-two. Look at the table in subsection A. Users — three. Folders — five. Card sets — seven. Cards — six. Let's take them one router at a time.

❒ But first — the outline covers HTTP status codes in subsection B. Why does that matter?

Because the status code is how the API communicates what happened. It's the language of API responses. Every response carries a numeric code. 200 range means success. 400 range means the client made an error. 500 range means the server broke.

We use seven specific codes. And I want to highlight a distinction that most beginners get wrong. Look at the table in your outline. 401 Unauthorized versus 403 Forbidden.

❒ They sound similar. What's the difference?

401 means "we don't know who you are." The user ID doesn't correspond to any registered user. Authentication failure. Your identity is unknown.

403 means "we know who you are, but you're not allowed." You're a real user. But you don't own this resource. Authorisation failure. Identity known. Permissions insufficient.

The other codes. 200 OK for successful reads, updates, deletes. 201 Created for successful creation. 404 Not Found when the resource doesn't exist. 409 Conflict when the data is valid but conflicts with current state. Like a duplicate username. And 422 when Pydantic validation fails.

❒ The outline also describes helper functions before the routers — four reusable verification functions in subsection C. Why?

Because ownership verification happens on almost every endpoint. Writing the same check inside twenty different functions is repetitive and error-prone. Instead, we extract it into helpers that every endpoint calls.

"verify_user" takes a user ID. Queries the users table. User doesn't exist? 401 Unauthorized.

"verify_folder_ownership" takes a folder ID and user ID. Fetches the folder. Doesn't exist? 404. Exists but the user doesn't match? 403.

"verify_cardset_ownership." Same pattern for card sets. 404 or 403.

❒ But cards don't have their own user underscore id. So how does card ownership verification work?

That's what the fourth helper solves. "get_card_and_verify_ownership." It performs a two-step chain. First, fetch the card. Doesn't exist? 404. Then look at which card set this card belongs to. Verify that the requesting user owns that card set. Doesn't own it? 403. Two database lookups chained together. Because card ownership is inherited, not direct.

❒ Alright. Let's go through the routers. User router first — three endpoints.

The simplest router. POST /users. Register a new user. Before inserting, the endpoint checks whether the username or email already exists. If either does? 409 Conflict. Clear message. "Username already taken."

❒ Why check explicitly? The database has UNIQUE constraints — wouldn't it catch duplicates?

It would. But the error message would be a raw database error. Cryptic. Unhelpful to the client. By checking explicitly first, we return a human-readable message. Better experience. Same protection.

GET /users. List all registered users. No authentication required for this tutorial.

GET /users/{user_id}. Get one specific user. Returns them or 404.

❒ Folder router — five endpoints. I'm looking at subsection E in the outline.

POST /cardfolders. Create a folder. Here's the critical line. "data['user_id'] = x_user_id." Ownership is set server-side. From the header. The client's request body doesn't contain "user_id" at all. Remember, it's excluded from the Create model. The client literally cannot claim to create a folder on behalf of another user. The system controls who owns what.

❒ That's the ownership enforcement pattern.

And it repeats everywhere. GET /cardfolders/my. Returns only folders where "user_id" matches the requester. Your folders. Nobody else's.

GET /cardfolders/{folder_id}. Get one folder by ID. 404 if not found.

PUT /cardfolders/{folder_id}. Update. Calls "verify_user" first. Then "verify_folder_ownership." Not the owner? 403 Forbidden.

DELETE /cardfolders/{folder_id}. Delete with cascades. Same ownership check. Delete a folder and all its card sets are destroyed. All the cards inside those sets too. The cascade chain we designed in Section III.

❒ Card set router — seven endpoints. This is the biggest router. Let's take them in logical groups.

Let's start with creation and retrieval. POST /cardsets. Create a card set. Two verifications before anything happens. The requesting user must exist. And the parent folder must exist and belong to that user. You can't create a card set inside someone else's folder.

GET /cardsets/my. All your card sets. Simple filter on "user_id."

❒ Now the public and visibility endpoints — this is where it gets interesting.

GET /cardsets/public. Returns everything where "is_public" is true. No authentication required. Anyone can browse public sets. Even an anonymous client with no header.

GET /cardsets/{cardset_id}. Get one specific card set. This is where the visibility logic kicks in. Notice something about the header. It's optional here. "Header(default=None)." Why?

❒ Because a public set should be viewable by anyone?

Exactly. If the set is public, return it. No matter who's asking. Even if there's no header at all. If the set is private? Now we check. Is the requester the owner? Yes? Return it. No? 403 Forbidden. One endpoint. One piece of branching logic. Handles both public and private access.

❒ What about viewing card sets within a specific folder?

GET /cardsets/folder/{folder_id}. Gets all card sets in a folder. But filtered. It fetches everything from that folder. Then filters in Python. Keep sets that are either public or owned by the requesting user. You see your own stuff plus anything public. Other people's private sets are invisible.

❒ Why filter in Python instead of in the database query?

Pragmatic reason. Supabase's chained query API doesn't easily support OR conditions. Like "where is_public equals true OR user_id equals X." For small to medium datasets, fetching all and filtering in Python is perfectly fine. For massive datasets, you'd use a stored procedure. But for this tutorial, in-memory filtering works.

❒ Now the write operations — update and delete.

PUT /cardsets/{cardset_id}. Update. Owner only. The usual ownership verification. And here's a crucial detail. The code uses "model_dump(exclude_unset=True)."

❒ What does that do?

It solves a subtle but devastating problem. The client sends an update. They only want to change the name. Nothing else. Without "exclude_unset," every field the client didn't mention gets sent as None to the database. Overwrites existing data. Your carefully written description? Gone. Your "is_public" flag? Reset to None.

With "exclude_unset=True," only fields the client actually included get sent. "I didn't mention the description" means leave it unchanged. "I explicitly set the description to null" means clear it. That distinction matters. And "model_dump" handles it correctly.

DELETE /cardsets/{cardset_id}. Owner only. Cascades to all cards inside.

❒ Card router — six endpoints. Subsection G.

POST /cards. Create a card. Verifies the user exists and owns the parent card set. Can't sneak cards into someone else's set. And here's a nice touch. If the client provides "front_text_1" but not "front_audio_text_1," the API automatically generates the audio text. Calls a function we'll build in Section VII. Same for back text. The client gets TTS-ready text for free.

❒ What about reading cards? How does visibility work at the card level?

GET /cards/{card_id}. Get one card. Card visibility is inherited from the parent card set. The endpoint looks up which set the card belongs to. Checks whether that set is public. Public? Anyone can see the card. Private? Only the owner. Making a card set private hides all its cards automatically. No per-card flags needed.

GET /cards/cardset/{cardset_id}. Get all cards in a set. Same visibility check. Applied once to the parent set.

❒ Now the update endpoint — this is where the audit trail happens, right?

PUT /cards/{card_id}. Update. Owner only. Plus audit trail. First, ownership verification through the two-step chain. Fetch the card. Verify the parent card set's owner. If the client changes the text but doesn't provide new audio text, it auto-regenerates. Then the two critical lines.

"data['updated_at'] = datetime.now(timezone.utc).isoformat()." That stamps the current UTC time as an ISO 8601 string. A format like "2025-03-15T14:30:00+00:00." Unambiguous. Machine-parseable across every language and system. UTC ensures every timestamp is in the same frame regardless of where the server runs.

"data['updated_by'] = x_user_id." Records who made the edit. Both fields from Python's built-in datetime module. No extra packages.

❒ And the remaining two endpoints?

DELETE /cards/{card_id}. Owner only. Two-step ownership chain.

GET /cards/cardset/{cardset_id}/updates. The audit history view. Instead of returning full cards with all content fields, it returns a lightweight view. Just "id," "cardset_id," "updated_at," and "updated_by." Think of it as a dashboard. Which cards were recently modified. And by whom. The SELECT call requests only those specific columns. More efficient for this overview purpose.

❒ Now let's open up the router code and look inside.

"user_router.py" is the simplest. Three endpoints. Three functions. No helper functions needed because users don't have ownership logic. The thing to notice? The duplicate check before insertion. Two separate queries. One for username. One for email. Each returns a human-readable error message.

"cardfolder_router.py" is where the pattern emerges. Five endpoints. Two helper functions at the top. "verify_user" and "verify_folder_ownership." Every write endpoint calls them first. The key line to pay attention to is in the create function. "data['user_id'] = x_user_id." That's where ownership gets stamped. Server-side. Not from the client body.

"cardset_router.py" is the most complex router. Seven endpoints. Two helpers. "verify_user" and "verify_ownership." This is where visibility logic lives. Look at Endpoint 4. The GET for a single card set. The header is optional there. "Header(default=None)." That's the difference between "you must be logged in" and "anyone can browse public content." Also look at Endpoint 6. The update. That's where "model_dump(exclude_unset=True)" appears. One line. Prevents accidental data destruction on partial updates.

"card_router.py" has four helper functions and six endpoints. The helpers form a chain. "verify_user" checks identity. "verify_cardset_ownership" checks the parent set. "get_card_and_verify_ownership" chains two lookups together. Fetch the card. Then check who owns the parent set. It's like asking: does this card exist? And then: does this person have the right to touch it? The update endpoint is the most interesting. That's where audio auto-generation and audit trail stamping both happen.

❒ Subsection H summarises key patterns across all routers. Two authentication patterns. Mandatory "Header(...)" for write operations. Optional "Header(default=None)" for reads that allow public access. Consistent error codes. 401, 403, 404, 409, 422. Ownership enforcement on every single write operation. Verify user. Verify ownership. Perform action. And visibility cascading from card set to cards. That's the entire endpoint layer.

---

---

## SECTION VII — AUDIO TEXT GENERATION WITH REGULAR EXPRESSIONS

---

❒ Section VII. Audio text generation. We mentioned earlier that display text and speech text are different. Let me understand the problem concretely.

Take a flashcard for learning Spanish. On screen, it shows "El gato (the cat) [m.]" Perfectly clear visually. "El gato" is the word. "(the cat)" is the English translation hint. "[m.]" tells you it's masculine. A human reader processes these three pieces instantly.

Now send that text to a text-to-speech engine. TTS engines read literally. Every character. Every punctuation mark. What you hear is: "El gato open parenthesis the cat close parenthesis open bracket m period close bracket." Unintelligible. Useless for language learning.

❒ So we need to strip out the visual formatting and keep just the speakable part.

Exactly. "El gato (the cat) [m.]" needs to become "El gato." Clean, natural, ready for speech. And we need to do this automatically, because asking users to manually create audio-friendly text for every card defeats the purpose.

❒ What tool do we use?

Regular expressions. Regex. Specifically, Python's "re.sub" function. If you haven't used regex before, here's the idea. Instead of searching for a specific string like "find the word cat," a regex describes a pattern. Like "find anything between square brackets." Python's "re" module provides the functions. "re.sub" is for substitution. Three arguments. The pattern to find. The replacement. Often an empty string, which effectively deletes the match. And the text to search within. Returns a new string.

❒ The outline lists five transformation rules in subsection C, applied in a specific order. Why does order matter?

Because each rule leaves behind artifacts that later rules clean up. If you run the cleanup step first, it has nothing to clean — and then the other rules create new messes. The sequence is deliberate. Let me walk through each rule, and then we'll trace a complete example.

❒ Rule one.

Remove square bracket content. The pattern matches an opening bracket, then any characters, as few as possible, then a closing bracket. Replace with empty string. "El gato [m.]" becomes "El gato" with a trailing space where the brackets were.

❒ Hold on — "as few as possible." What's the question mark doing?

This is the greedy versus non-greedy distinction. It's critical. By default, regex is greedy. It matches as many characters as possible. If your text is "[one] word [two]" and you use a greedy pattern, it matches from the first opening bracket all the way to the last closing bracket. "[one] word [two]" as a single match. The word between gets swallowed.

The question mark makes it non-greedy. Match as few characters as possible. Now it matches "[one]" first. Then "[two]" separately. The word between is preserved. For flashcards with multiple bracketed annotations, non-greedy is essential.

❒ Rule two.

Remove parenthetical content. Same approach, same non-greedy matching. "El gato (the cat)" becomes "El gato" with a trailing space.

❒ Rule three — this one's different.

Right. Language flashcards sometimes show alternatives with a slash. "rojo/a" means the masculine form "rojo" or the feminine form "roja." For audio, we want only the first form.

This rule uses a capture group. Parentheses in the regex capture a portion of the match. The pattern captures one or more word characters, then a slash, then more word characters. The replacement is a backreference. It means "put back whatever was in the first capture group."

❒ Wait — how does Python handle that backslash 1?

In Python, you write it with an "r" prefix. A raw string. This matters. Without the "r" prefix, Python's string parser would interpret the backslash as a special character before the regex engine ever sees it. The raw string tells Python to pass the backslash through untouched. The regex engine then interprets it as a backreference. Two layers of interpretation. You need the raw string to bypass the first one.

So "rojo/a" becomes "rojo." The first form is kept, the slash and everything after it is discarded.

❒ Rule four.

Remove leading numbers. Matches digits followed by a dot at the start of the string. "3. El gato" becomes "El gato" with a leading space.

❒ And rule five — the cleanup.

This must be last. Every previous rule removed content but left gaps. Extra spaces where brackets, parentheses, slashes, and numbers used to be. Rule five collapses multiple consecutive spaces into a single space. Strips leading and trailing whitespace. If you ran this earlier, the gaps from subsequent rules would remain uncleaned.

❒ Let's trace the complete example from the outline. Subsection D has a table — I'm looking at it now.

Input: "3. El gato rojo/a (the red cat) [m./f.]"

After rule one — brackets gone: "3. El gato rojo/a (the red cat)" with trailing space.

After rule two — parentheses gone: "3. El gato rojo/a" with extra spaces.

After rule three — slash simplified: "3. El gato rojo" with extra spaces.

After rule four — leading number gone: "El gato rojo" with leading and extra spaces.

After rule five — whitespace cleaned: "El gato rojo."

Clean, natural, ready for TTS. From a visually rich flashcard string to a speakable sentence, automatically.

❒ How does this integrate with the card router?

The function is called automatically when a client provides display text but not the corresponding audio text field. If they don't supply "front_audio_text_1," the API generates it. If they do supply it, their explicit value takes priority. Auto-generation is a default. Not a mandate.

And it's extensible. Adding a new rule is just another "re.sub" line at the appropriate position. Keep the whitespace cleanup at the end.

❒ Let's look at the actual code for this.

Open "utils/audio_text.py." One function. "generate_audio_text." Takes a string, returns a string. Inside, you'll see five "re.sub" calls in sequence. Each one is a single line. Pattern, replacement, text. That's it. Five lines of regex doing all the heavy lifting. The whole file is about 30 lines including comments.

The thing to notice? Each regex rule has detailed comments explaining every part of the pattern. What the backslash does. What the question mark does. What the capture group captures. These comments are there because regex is notoriously hard to read. The code is simple. The patterns are not. The comments bridge that gap.

Also notice that the function is pure. It takes a string in. Returns a string out. No database calls. No side effects. It's a utility. The card router calls it. But this function doesn't know or care about cards, routers, or databases. Clean separation.

❒ Section summary. Five rules in strict order. Non-greedy matching prevents overmatching. Capture groups and backreferences for partial replacement. Whitespace cleanup last. Auto-generation is automatic but overridable. Onto the final major feature.

---

---

## SECTION VIII — PUBLIC SHARING AND THE COPY FEATURE

---

❒ Section VIII. The copy feature. We've built public visibility. We've built ownership. Now what happens when those two collide? A student finds a great public card set. Can't do anything with it except look.

Exactly the problem. The outline has this scenario in subsection A. A Spanish teacher spends hours building "DELE B2 Vocabulary." 200 carefully crafted cards. Audio text. Image URLs. Everything polished. She marks it public. Students find it. Love it. But a student wants to personalise. Add notes. Tweak translations. Remove cards they already know.

The student can't edit the original. They're not the owner. And even if we gave them permission? Their changes affect every other student using the same set. One person's customisation destroys the experience for everyone else.

❒ So we need a way to create a personal copy.

A deep copy. Not just the card set metadata. Every single card inside. Duplicated into the student's own account. Their copy. Their property. Completely independent from the original. The teacher's set untouched.

❒ The outline describes a five-step process in subsection B. Walk me through it.

Step one. Verify the source card set exists and is accessible. It must be either public or owned by the requester. Yes, you can copy your own sets. Useful for creating variations.

Step two. The user specifies a target folder via a query parameter called "target_folder_id." That folder must exist. And it must belong to the requesting user. You can't copy into someone else's folder.

Step three. Create a new card set record. Name is "Copy of" followed by the original name. Owner is the requester. Folder is the target folder. "is_public" is false. Your copy starts private.

Step four. Fetch all cards from the source card set.

Step five. Duplicate every card into the new set.

❒ What exactly gets preserved, and what starts fresh?

Look at the table in your outline. Subsection B point two. There's a clear split. Preserved exactly? All eight content fields. Front text, front audio text, front audio, front image. Same four for back. The educational content crosses over perfectly.

Starting fresh? The "id." Each card gets a new UUID. The "cardset_id." Points to the new set, not the original. "created_at." Set to now by the database. "updated_at." Null. This copied card has never been edited. Only created. "updated_by." Null. No edits have occurred.

❒ The endpoint itself — what does the URL look like?

POST /cardsets/{cardset_id}/copy with "target_folder_id" as a query parameter. POST because we're creating new data. The cardset_id in the URL is the source. The query parameter tells us where the copy goes.

❒ The outline mentions a defensive programming pattern — dot get versus bracket access. What's that about?

When reading fields from the source cards to build the copies, the code uses "card.get()" with the field name instead of bracket access. If a field doesn't exist or isn't populated? That's valid. Not every card has all eight fields. ".get()" returns None gracefully. Bracket access would crash with a KeyError. Defensive coding. Handle partial data without special-casing each field.

❒ And there's a performance consideration?

A big one. Instead of inserting cards one by one, all the new cards are collected in a list and inserted with a single call. Supabase's insert method accepts a list of dictionaries. Copying 200 cards? One network call. Not 200. Over a network with any latency at all, that's the difference between a fraction of a second and an unacceptable wait.

❒ The outline has a full end-to-end test scenario in subsection D. Can we walk through it? I want to see the whole system working together.

Let's trace it. Two users, two folders, and we'll watch ownership, visibility, copying, and audit trails all interact.

First, register two users. "teacher_ana" and "student_bob." Each gets a user ID back. Teacher creates a folder called "Languages." Student creates "My Studies."

Teacher creates a card set called "Spanish Basics" inside her Languages folder. "is_public" set to true. She creates a card. Front text "El gato (the cat) [m.]" Back text "The cat." The API auto-generates the audio text. "El gato." All the regex rules we just discussed. Working automatically.

❒ Now the student enters the picture.

The student calls GET /cardsets/public. No header needed. There's "Spanish Basics" in the results. The student copies it. POST to the copy endpoint with the target folder set to "My Studies." Response? "Copy of Spanish Basics." Owned by the student. Private.

❒ And now the student can personalise it.

The student calls GET /cardsets/my. "Copy of Spanish Basics" appears. Gets all the cards from the new set. Picks one. Updates it. Changes front text to "El gato gordo (the fat cat)." The API stamps "updated_at" with the current timestamp. "updated_by" with the student's ID. And auto-regenerates the audio text as "El gato gordo."

❒ Here's the critical test — is the teacher's original untouched?

GET the cards from the original set. Every single card is exactly as the teacher left it. No modifications, no timestamps, no sign that a copy ever happened. The two sets are completely independent.

And if the student tries to directly edit one of the teacher's cards? PUT on the teacher's card ID with the student's header. 403 Forbidden. "You do not own the parent card set." The ownership system works exactly as designed.

❒ Let's peek at the copy endpoint code itself.

It's added to "cardset_router.py." One function. "copy_cardset." About 40 lines. The five steps we just discussed map directly to five blocks of code. Each block has a comment. Step 1: fetch the source and check accessibility. Step 2: verify the target folder. Step 3: create the new card set. Step 4: fetch source cards. Step 5: build the list and batch insert.

Two things to notice. First, the new card set is built as a dictionary. Not from a Pydantic model. Because we're constructing it server-side with known-good data. No client input to validate. Second, the batch insert at the end. All cards go into a list. One call to "supabase.table('cards').insert(new_cards)." One database call. Not one per card.

❒ Section summary. Deep copy. Content preserved. Metadata fresh. Only public or owned sets copyable. Target folder must be yours. Batch insert for performance. Complete independence. That's a proper multi-user platform. One more section to go.

---

---

## SECTION IX — FINAL SUMMARY

---

❒ Section IX — the final summary. Let's take stock. What have we built?

Look at subsection A in your outline. There's a table listing every file. Thirteen source files plus three init files. ".env" and ".gitignore" for configuration. "database.py" for the Supabase connection. "main.py" as the orchestrator. Four model files. Four router files. One audio text utility. Twenty-two endpoints plus one root health check.

❒ And the multi-user features — subsection B has the complete list.

Nine items. User registration and lookup. Folder ownership with cascading deletes. Card set ownership. Same pattern. Ownership enforcement on every write operation across every entity. Public/private visibility through the "is_public" flag. Visibility filtering on every read operation. Card-level audit trail. Deep copy with batch duplication. Simplified authentication via the "x-user-id" header.

❒ How do we actually run it?

Three commands. They're in your outline at subsection C. "cd flashcard-api." "workon vintel." "uvicorn main:app --reload." Open localhost:8000/docs in your browser. Every endpoint is there. Interactive. Testable.

❒ The outline closes with four things to remember above all else. Let's end with those — they're in subsection D.

First. The data hierarchy. Users. Cardfolders. Cardsets. Cards. Ownership flows down from users. Visibility is controlled at the card set level. Cascades to all cards within. Not at the folder level. Not at the card level. The card set level.

Second. CASCADE versus SET NULL. CASCADE means the child can't exist without the parent. Destroy them together. SET NULL means the reference is informational. Clear it, but the child survives. Every foreign key in this project uses one or the other. The choice is never arbitrary.

Third. The API controls the audit trail. Not the client. "updated_at" and "updated_by" are set automatically by the server during updates. They never appear in Create or Update request bodies. No one can fake when or by whom an edit was made.

Fourth. Deep copy means complete independence. Content is preserved exactly. IDs, timestamps, audit fields all start fresh. Edits to the copy never affect the original. Edits to the original never affect the copy. Two independent objects that happen to have the same content at the moment of creation.

❒ And that's the whole outline — nine sections, four database tables, twenty-two endpoints, a regex engine, and a multi-user platform. If you've been following along with the printed outline, every principle, every table, every bullet point has been discussed. Go back to any section that needs another pass. The outline and this podcast are built to work together.

Thanks for sticking with us. Go build something.
