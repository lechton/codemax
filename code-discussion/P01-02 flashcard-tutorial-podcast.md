# Building a Flashcard API from Zero — Podcast Script

---

## SECTION 1 — WHY FASTAPI AND WHAT PROBLEM DOES IT SOLVE

---

❒ So we're building a flashcard API today — but before we even touch code, what's the actual problem we're solving here?

Alright so picture this. You've written a Python script on your laptop. It reads a JSON file, it processes some flashcard data, and it prints stuff to the terminal. Great. Works fine when you're sitting there running it yourself. But now imagine you want a phone app to show those flashcards. Or a web browser. Or someone on a completely different machine wants to access the same data. Your Python script can't do that. It runs once, it finishes, it's done. There's no door for the outside world to knock on. Nobody can reach your data. That's the core problem.

❒ Okay, but couldn't you just throw the JSON file on a web server and let people download it?

You could, technically. But then it's read-only. Your users can look at the flashcards, sure, but they can't create new ones, they can't edit existing ones, they can't delete anything. It's just a static file sitting there. What you actually need is a living, breathing program that sits on a server, waits for requests to come in, processes them, talks to a database, and sends back responses. That living program — that's what we call an API. Application Programming Interface.

❒ So what does an API actually look like in practice? How does someone interact with it?

An API exposes what we call endpoints. An endpoint is just a specific URL. Like, you'd have something like localhost colon 8000 slash cardfolders. And depending on how you access that URL — which HTTP method you use — it does a different thing. You use GET to retrieve data. POST to create new data. PUT to update something that already exists. DELETE to remove it. Those four operations — Create, Read, Update, Delete — we call that CRUD. And they map directly to those four HTTP methods.

❒ There are different frameworks for building APIs in Python, right? Why did we pick FastAPI specifically?

Yeah, Flask is probably the most well-known one. Django REST Framework is another big one. But FastAPI wins for us for three specific reasons. The first one is automatic data validation. When someone sends data to your API — say a new flashcard — you need to check that data before it hits your database. Is the front text actually a string? Is the image URL valid? In Flask you'd write all that checking code by hand. FastAPI uses a library called Pydantic that does it automatically. You just define a model that says "this field must be a string, this field is optional," and FastAPI rejects bad requests before your code even runs.

❒ That sounds like it saves a lot of boilerplate. What's the second reason?

Automatic documentation. The moment you start your FastAPI server, it generates an interactive web page at localhost colon 8000 slash docs — it's called Swagger UI, by the way. FastAPI reads your Python type hints and your Pydantic models and uses them to automatically build this whole interactive page. You can see every single endpoint, what data each one expects, and you can literally test them right there in your browser. You don't need Postman, you don't need curl — it's all built in. When you're learning or debugging, that's incredibly valuable.

❒ And the third reason?

Speed and modern Python. FastAPI uses Python type hints natively. If you write front underscore text underscore 1 colon str in your function, FastAPI uses that type hint for both validation and documentation at the same time. The framework also supports async, meaning it can handle many requests at the same time without blocking. We'll use synchronous code in this tutorial because it's simpler to learn, but the capability is there.

❒ Now, we're using something called Supabase for the database. Why not just a local SQLite file?

Good question. Supabase is a hosted PostgreSQL database that comes with a web dashboard and client libraries for Python, JavaScript, and other languages. You create your tables in a nice web interface, and then from your Python code you call things like supabase dot table cards dot select star dot execute to read data. Now, SQLite would technically work for a personal project. But Supabase gives us three things. First, the database is accessible from anywhere — not just your laptop. Second, it has a visual dashboard where you can see your data in real time. And third, its Python client library is really clean. When you later deploy your API to a server, the Supabase connection works exactly the same — no migration needed.

❒ You mentioned this is a multi-user system. What does that actually mean for us?

It means the flashcard API isn't just for one person — it serves many users. And that introduces three problems that a single-user system never has to deal with. Problem one is ownership. If User A creates a card set called Spanish Verbs, User B shouldn't be able to edit or delete it. Every card set needs an owner, and every write operation has to check whether the person making the request is actually the owner.

❒ Makes sense. What's problem two?

Visibility. Maybe User A wants to keep their card set private — only they can see it. But maybe they also have an amazing set called JLPT N5 Kanji that they want to share with everyone. So we need a flag on each card set — is underscore public — that controls whether other users can see it. Private sets are invisible to everyone except the owner. Public sets are browsable by all.

❒ And the third problem?

Audit trails. When a card gets updated, you want to know when it was updated and who did it. If something goes wrong — a card's text gets corrupted, someone makes an accidental edit — you need a trail showing the last modification timestamp and the user responsible. So every card will carry updated underscore at and updated underscore by fields.

❒ Is there anything else that comes out of having public visibility?

Yeah, there's a fourth feature that follows naturally — copying. If User B sees User A's public card set and wants their own version so they can modify it, add cards, track their own progress, the API should support a one-click copy operation. It duplicates the entire card set and all its cards into User B's account. So these four features — ownership, visibility, audit trails, and copying — they turn our flashcard API from a single-user toy into a real multi-user platform. And they'll be woven into every section of this tutorial.

❒ Quick recap — what have we decided so far?

We need an API because static files can't handle CRUD operations from external applications. We chose FastAPI because it gives us automatic validation through Pydantic, automatic documentation, and modern Python type hints. We chose Supabase because it gives us a hosted PostgreSQL database with a visual dashboard and a clean Python client. And we introduced the multi-user problem: ownership, visibility, audit trails, and copying. We've got eight sections ahead of us. Section 1 is done. Let's move on.

---

---

## SECTION 2 — ENVIRONMENT SETUP ON macOS

---

❒ Alright, Section 2 — we're setting up the environment. What's the game plan here?

Four steps, nice and clean. First, we create a project folder and activate our Python virtual environment. Second, we install FastAPI, Uvicorn, and the Supabase client. Third, we create a dot env file for our Supabase credentials. Fourth, we verify everything works with a quick test run. After this section you'll have a working folder on your Mac with everything installed and ready to go.

❒ Let's start. How do we create the project folder and activate the virtual environment?

Open your Terminal. Type these commands one at a time. First, mkdir flashcard-api — that creates the folder. Then cd flashcard-api — that moves you into it. Then workon vintel — that activates the virtual environment. After you run that last one, your terminal prompt will change. You'll see the word vintel in parentheses at the beginning. That means you're inside the virtual environment.

❒ What exactly is a virtual environment? Why do we need one?

Think of it as an isolated Python installation managed by virtualenvwrapper. The workon command activates a named environment stored in a central location — typically the dot virtualenvs folder in your home directory — keeping your project folder clean. When you install libraries while the virtual environment is active, they go into that central environment, not into your system Python. So your flashcard project's dependencies will never conflict with another project's dependencies. One important thing to remember — every time you open a new terminal window to work on this project, you have to run workon vintel again. The activation doesn't persist between terminal sessions.

❒ Got it. Now what do we install?

With your virtual environment active — you should see vintel in parentheses — run pip install fastapi uvicorn supabase python-dotenv. That single command installs four packages.

❒ Can you break down what each one does?

Absolutely. Fastapi is the web framework itself. It gives you the decorators like at app dot get and at app dot post that turn your Python functions into API endpoints. Uvicorn is what's called an ASGI server — that stands for Asynchronous Server Gateway Interface. Think of it as the engine that actually runs your FastAPI application. FastAPI by itself is just a set of rules and decorators — it can't listen for HTTP requests on its own. Uvicorn is the piece that listens on a port — port 8000 by default — receives incoming requests, hands them to FastAPI for processing, and sends the responses back. Supabase is the official Python client library for talking to your Supabase database. And python-dotenv is a small utility that reads a dot env file and loads its contents as environment variables. So later in your code, you can access them with os dot environ bracket SUPABASE underscore URL bracket. That's how we keep our credentials out of our source code.

❒ Speaking of credentials — how do we set up that dot env file?

In the root of your flashcard-api folder, create a file called dot env — notice the dot at the beginning, that makes it a hidden file on macOS. Inside it you put two lines. The first one is SUPABASE underscore URL equals and then your project URL. The second is SUPABASE underscore KEY equals and then your anon key.

❒ Where do I find those values?

Go to your Supabase dashboard at supabase dot com, open your project, click on Project Settings in the left sidebar, then click API. You'll see two values right there — the Project URL and the anon public key. Copy those into your dot env file. And here's the important part — also create a dot gitignore file in your project root. Inside it, put two lines: dot env, and double underscore pycache double underscore slash. This tells Git to ignore your secrets file and Python's cache files. You never want your credentials ending up on GitHub.

❒ How do we verify everything is working?

Create a quick test file called test underscore setup dot py in your project root. Inside it, import FastAPI, create an app instance, and add one endpoint that returns a simple message like "Flashcard API is alive." Then run uvicorn test underscore setup colon app dash dash reload. Open your browser, go to localhost colon 8000, and you should see that JSON message. Then go to localhost colon 8000 slash docs and you'll see the interactive Swagger documentation with one endpoint listed.

❒ What does that uvicorn command actually mean?

The format is uvicorn followed by filename without extension colon variable name. So test underscore setup colon app tells Uvicorn to look inside test underscore setup dot py for an object called app. The dash dash reload flag means Uvicorn watches your files for changes and automatically restarts the server whenever you save. Super useful during development. When you're done testing, press Control C to stop the server, and you can delete that test file — it was only for verification.

❒ Quick recap of Section 2?

We did four things. Created the project folder and activated our virtual environment with workon vintel. Installed four packages — fastapi, uvicorn, supabase, and python-dotenv. Created a dot env file with our Supabase credentials and a dot gitignore to protect them. And verified everything by running a tiny test server. Our project folder right now has the dot env file and the dot gitignore. That's all we need. On to Section 3.

---

---

## SECTION 3 — DATABASE DESIGN IN SUPABASE

---

❒ Section 3 — we're designing the database now. How many tables do we need?

Four tables. Users, cardfolders, cardsets, and cards. And the order matters here — we'll see why in a moment.

❒ Before we create them, can you walk me through the data hierarchy? How do these tables relate?

Sure. At the foundation you have users. A user is someone who registers with the system — they have a unique ID, a username, and an email. Users own things. Moving up, you have card folders. A folder is a container that groups related collections of cards. Think of a folder called Spanish Vocabulary or Medical Terms. Each folder is owned by exactly one user. Inside each folder you have card sets. A card set is a specific collection of flashcards within that folder. So your Spanish Vocabulary folder might have card sets like Food Words, Colors, and Verbs. Each card set is also owned by one user, and each one has that is underscore public flag — if it's true, anyone can see it. If it's false, only the owner can. And inside each card set you have the actual cards with front and back content.

❒ Why not just throw everything into one giant table? One row per card with the folder name, set name, and owner name right there in each row?

It would technically work, but it creates serious problems. Problem one — data duplication. If a folder called Spanish Vocabulary has 500 cards across 10 sets, the string "Spanish Vocabulary" appears 500 times. Want to rename the folder? You're updating 500 rows instead of one. Problem two — deletion anomalies. If you delete all cards in a set, the set itself vanishes because there's no row left. Maybe you wanted to keep that empty set as a placeholder. Problem three — inconsistency. One row says Spanish Vocabulary, another says Spanish Vocabulay with a typo. Which is correct? And problem four — user data duplication. Without a separate users table, every card repeats the user's name and email. User changes their email? Update every card they ever touched.

❒ So how do we fix all that?

The solution is normalization — splitting data into separate tables where each fact is stored exactly once. The folder name lives once in the cardfolders table. The user's data lives once in the users table. Everything else just stores a reference — what we call a foreign key — pointing to the right parent record.

❒ Hold on — what exactly is a foreign key?

A foreign key is simply a column in one table that references the primary key of another table. It's what establishes the parent-child relationship between them. So when the cardfolders table has a user underscore id column, that column holds a value that matches an id in the users table. That's the link. The database enforces this — you can't put a random value in there that doesn't correspond to an actual user. The foreign key is the glue that connects tables together in a normalized design.

❒ You mentioned there are special multi-user columns. What are those?

Three categories. First, ownership columns. Both cardfolders and cardsets get a user underscore id column that points to the users table. That answers "who owns this?" Every write operation checks this column against whoever's making the request. If they don't match, the API returns a 403 Forbidden. Second, visibility columns. Cardsets gets an is underscore public boolean that defaults to false. Private by default, the owner can flip it to public when they're ready to share. Third, audit columns. The cards table gets updated underscore at and updated underscore by. Every time a card gets modified, we record when and who.

❒ Alright, let's actually create these tables. How do I do it in Supabase?

It's really easy, just pay attention. First, you go to your Supabase dashboard — supabase dot com — and open your project. On the left sidebar, you'll see a bunch of options.

❒ There are a lot of options in that sidebar, right?

Yeah, you'll see things like Authentication, Database, Storage, and others. The one you want is Table Editor. Click on that. Once you're in the Table Editor, you'll see a button that says New Table. That's where we start. We're going to create four tables, and the order matters because some tables reference others. You can't reference a table that doesn't exist yet.

❒ Let's start with the first table. Which one do we create first?

The users table — because the other tables are going to point back to it. So click New Table, and for the name type users. Now, you'll see a checkbox that says Enable Row Level Security. For now, uncheck that — we'll deal with security later. Then you need to add the columns.

❒ How do I add columns? Is there a button or something?

Right there in the table creation screen you'll see an area to add columns. There might already be a default id column — Supabase often adds that for you. If it does, make sure the type is set to uuid and the default value is gen underscore random underscore uuid with parentheses. That automatically generates a unique ID for every new row. Then you click Add Column to add the next one.

❒ What columns does the users table need?

Four columns total. The id we just talked about — uuid, primary key, auto-generated. Then username — set the type to text, and make sure it's marked as NOT NULL. Then email — also text, also NOT NULL. And finally created underscore at — set the type to timestamptz, and the default value to now with parentheses. That automatically stamps the creation time.

❒ You mentioned username and email need to be unique. Where do I set that?

Good catch. After you create the columns, you need to go into the column settings for username — there should be a gear icon or an option to edit the column — and check the Is Unique box. Do the same for email. Those UNIQUE constraints mean the database itself will reject any attempt to register a duplicate username or email. That protection happens at the database level, not just in our Python code.

❒ Great. What's the second table?

Cardfolders. Same process — click New Table, name it cardfolders, uncheck Row Level Security for now. This table gets five columns. The id column — uuid, primary key, auto-generated, same as before. Then user underscore id — this is the important one. Set the type to uuid, mark it NOT NULL. Now here's the key step — you'll see a little link icon or a Foreign Key option next to the column.

❒ What does that link icon do?

That's how you create the foreign key relationship. Click it, and it'll ask you which table and column you want to reference. You select the users table and the id column. Then it'll ask about the delete behavior — you want ON DELETE CASCADE. That means if a user gets deleted, all their folders automatically get deleted too. No orphaned data.

❒ What are the other columns for cardfolders?

Name — text, NOT NULL. Description — text, but leave it nullable, it's optional. And created underscore at — timestamptz with default now. That's it for folders.

❒ Third table?

Cardsets — and this one's the most interesting because it has the multi-user columns. Click New Table, name it cardsets. This table gets seven columns. The id — same as always, uuid, primary key, auto-generated. Then cardfolder underscore id — uuid, NOT NULL, and you click that link icon again to reference cardfolders dot id with ON DELETE CASCADE. So deleting a folder cascades and deletes all its card sets too.

❒ What about the ownership column?

That's user underscore id — uuid, NOT NULL. Click the link icon, reference users dot id, again with ON DELETE CASCADE. This is the ownership link. Every card set belongs to exactly one user. If that user's account gets deleted, their card sets go with them.

❒ And the visibility flag?

That's is underscore public. Set the type to bool — you'll see boolean as an option in the type dropdown. Mark it NOT NULL, and set the default value to false. So when someone creates a card set, it's private by default. They have to explicitly make it public. Then you've got name — text, NOT NULL. Description — text, nullable. And created underscore at — timestamptz, default now.

❒ Last table — cards. This is the one with the audit trail, right?

Exactly. Click New Table, name it cards. This one has the most columns — thirteen in total. The id — uuid, primary key, auto-generated as always. Then cardset underscore id — uuid, NOT NULL, foreign key referencing cardsets dot id with ON DELETE CASCADE. Delete a card set, all its cards go with it.

❒ Then all the content fields?

Right. Eight content fields, all text type, all nullable — because a card might only have some of them filled in. You've got front underscore text underscore 1, front underscore audio underscore text underscore 1, front underscore audio underscore 1, front underscore image. Then the same four for the back — back underscore text underscore 1, back underscore audio underscore text underscore 1, back underscore audio underscore 1, back underscore image.

❒ And the audit columns?

Two of them. First, created underscore at — timestamptz, default now. That one never changes after the card is created. Then updated underscore at — timestamptz, but leave the default empty, no default. It starts as null. That null clearly says "this card has never been edited, only created." Every time someone updates the card, our API sets this to the current timestamp.

❒ What about updated underscore by?

That's the last column. Set it to uuid, leave it nullable. Now here's an important difference — click the link icon to reference users dot id, but this time choose ON DELETE SET NULL, not CASCADE.

❒ Wait, why SET NULL instead of CASCADE here?

Great question. Think about it — if the user who last edited a card gets deleted from the system, you don't want to delete the card itself. That would be data loss. The card data is still perfectly valid, it's just that the person who last touched it no longer has an account. So instead of deleting the card, we just clear the reference — set updated underscore by to null. It basically means "the user who last edited this card no longer exists." The card is preserved. Compare that with cardset underscore id where CASCADE makes sense — a card literally cannot exist without a card set, so if the set goes, the cards should go too.

❒ So the rule of thumb is CASCADE when the child can't exist without the parent, and SET NULL when it's just a reference?

Exactly. "This entity cannot exist without its parent" — use CASCADE. "This is just a reference for informational purposes" — use SET NULL.

❒ Can you give me the big picture of how all four tables connect?

Users sit at the top. A user can own many folders. Each folder can contain many card sets. Each card set belongs to one user and one folder. Each card set contains many cards. If a user deletes their account, it cascades — their folders get deleted, which deletes their card sets, which deletes their cards. But if a user only edited someone else's card, that card survives — the updated underscore by field just becomes null.

❒ Section 3 recap?

Four tables — users for identity, cardfolders owned by users, cardsets with ownership and a public-private flag, and cards with the actual content plus audit fields. Normalization prevents data duplication. Foreign keys with CASCADE enforce that deleting a parent removes its children. The is underscore public boolean controls visibility at the card set level — and it's important that it's at the card set level, not the folder level, because if you put visibility on folders you'd get contradictions, like a public card set inside a private folder. Keeping it on card sets avoids all that ambiguity. And updated underscore at plus updated underscore by give us an edit audit trail. Three sections down, five to go.

---

---

## SECTION 4 — PROJECT ARCHITECTURE

---

❒ Section 4 — project structure. Why can't we just put everything in one file?

Because it would get enormous. We'll have CRUD operations for users, folders, card sets, and cards, plus ownership checks, visibility filters, and the copy feature. That's over 20 endpoints. One file with 20-plus functions, all the imports, all the helper logic — it becomes unreadable very quickly.

❒ So how does FastAPI handle splitting code across files?

With something called routers. A router is basically a mini-application that handles a subset of endpoints. You create one router for user endpoints, one for folders, one for card sets, one for cards. Each router lives in its own file. Then in your main application file, you include all of them. Instead of writing at app dot get slash cardfolders, you write at router dot get slash cardfolders. The router isn't a standalone application — it needs to be plugged into the main FastAPI app using app dot include underscore router.

❒ What does the complete folder structure look like?

At the top level you have your flashcard-api folder. Inside it — dot env, dot gitignore, main dot py, database dot py. Then three subfolders. A models folder with an init file and four model files — user underscore models, cardfolder underscore models, cardset underscore models, card underscore models. A routers folder with an init file and four router files — same naming pattern. And a utils folder with an init file and audio underscore text dot py.

❒ What do those init files do? The double underscore init double underscore dot py ones?

They make each directory a Python package, which lets you do imports like "from routers import cardfolder underscore router." They can be completely empty — they just need to exist.

❒ What does each piece of the structure handle?

Main dot py is the entry point — it creates the FastAPI app, includes all four routers, and that's it. Uvicorn runs this file. Database dot py establishes the connection to Supabase — reads the dot env file, creates a client, exports it for everyone else to use. The models folder has Pydantic models that define the shape of data for each entity. The routers folder has the actual endpoint logic. And the utils folder has helper functions, like our audio text generator.

❒ Let's look at the two foundational files. What goes in database dot py?

Short and sweet. You import os, import load underscore dotenv from dotenv, import create underscore client and Client from supabase. Then you call load underscore dotenv to read the dot env file, pull out the two environment variables for URL and key, and create a Supabase client. That client object — stored in a variable called supabase — is what every router will import to talk to the database.

❒ And main dot py?

Also pretty short. Import FastAPI, import all four routers. Create the FastAPI app with a title, description, and version — we're using version 2.0.0 to reflect the multi-user feature set. Then four lines of app dot include underscore router to plug in each router. And a simple root endpoint that returns "Flashcard API is running" as a health check. When you run uvicorn main colon app dash dash reload, Uvicorn finds the app object in main dot py, and all the endpoints from all four routers are available.

❒ Section 4 recap?

We split code into files using FastAPI's APIRouter — one router per entity. Models folder for data shapes, routers folder for endpoint logic, utils folder for helpers. Database dot py creates the Supabase connection, main dot py ties everything together. And one thing worth noting — compared to a single-user system, the key additions here are the user underscore router dot py and user underscore models dot py files. Multi-user means we need a whole entity just for managing users. Four sections done, four to go.

---

---

## SECTION 5 — PYDANTIC MODELS

---

❒ Section 5 — Pydantic models. Why do we need these?

When someone sends a POST request to create a flashcard, they send JSON in the body. That JSON might look correct, or it might have a number where a string should be, or include fields that don't exist in our schema. Without validation, bad data hits your database and either causes errors or silently corrupts things. Pydantic prevents that. You define a class that describes the exact shape of acceptable data, and FastAPI uses it to validate every incoming request before your code even runs. Bad data? Automatic 422 response with a detailed error message.

❒ I've seen you mention Create models, Update models, and Response models. What's the difference?

Create models define what the client sends when making something new. They don't include auto-generated stuff like id or created underscore at — the database handles those. Update models define what can be changed after creation. Some fields might be excluded — like you shouldn't be able to change a card set's owner through an update. Response models define what the API sends back. They do include id, timestamps, audit fields — the client needs to see those.

❒ Let's go through each entity. What do the user models look like?

Simplest ones. UserCreate just needs username and email — both required strings. UserResponse adds id and created underscore at on top of that. We don't have a UserUpdate model — for simplicity we're not supporting changing usernames or emails in this tutorial.

❒ What about folder models?

CardfolderCreate has name, which is required, and description, which is optional and defaults to None. Notice that user underscore id is not in the Create model — it gets set from the request header in the router, so clients can't create folders pretending to be someone else. CardfolderResponse adds id, user underscore id, and created underscore at so the client can see who owns the folder.

❒ Card set models must be more interesting with the multi-user stuff?

Definitely. CardsetCreate has cardfolder underscore id, name, optional description, and is underscore public which defaults to False. So card sets are private by default. And again — no user underscore id in the Create model. The owner comes from the authenticated header. If you let the client set user underscore id in the body, anyone could claim to create sets on behalf of another user.

❒ Is there a CardsetUpdate model?

Yes. It lets you change name, description, and is underscore public — all optional, because you might only want to change one of them. It does not include cardfolder underscore id or user underscore id. You can't move a set to a different folder or transfer ownership through a simple update.

❒ And the card models? Those have the audit fields, right?

Right. CardCreate has cardset underscore id plus the eight content fields — front text, front audio text, front audio URL, front image, and the same four for the back. All optional because a card might only have some fields populated. CardUpdate has just the eight content fields, no cardset underscore id — you can't move a card to a different set. And CardResponse adds id, created underscore at, updated underscore at, and updated underscore by. Those last two are optional — they're null for brand new cards that have never been edited.

❒ Important detail — updated underscore at and updated underscore by are not in CardCreate or CardUpdate?

Exactly. The API sets those automatically. The client should never control audit trail data directly. When an update happens, the API stamps the current time and the current user. No one gets to fake their audit trail.

❒ How does the API know which user is making a request?

In a production system you'd use JWT tokens or OAuth or Supabase Auth. For this tutorial we're keeping it simple — the client sends their user underscore id as an HTTP header called x-user-id with every request. In FastAPI, you read it using the Header dependency. You write x underscore user underscore id colon str equals Header with an ellipsis, and FastAPI automatically looks for the header x-user-id. The ellipsis means it's required — the request fails with 422 if the header is missing.

❒ Wait — the variable uses underscores but the header uses hyphens?

Yeah, FastAPI automatically converts. Your Python variable x underscore user underscore id maps to the HTTP header x-user-id. That's because HTTP headers conventionally use hyphens, but Python variables can't have hyphens. FastAPI handles the translation.

❒ Is this header approach secure for production?

No — anyone could fake the header. But it lets us focus on the ownership and visibility logic without getting bogged down in authentication infrastructure. The concepts are identical regardless of how you identify the user. Only the mechanism for extracting the user ID changes.

❒ Section 5 recap?

We built Pydantic models for all four entities. User underscore id is never in Create models — it comes from the header. Card sets include is underscore public defaulting to false. Card responses include the audit trail fields. We introduced simplified auth through the x-user-id header using FastAPI's Header dependency. Five down, three to go.

---

---

## SECTION 6 — BUILDING EVERY ENDPOINT

---

❒ Section 6 — the big one. How many endpoints are we building?

Twenty-one across four routers. Three for users, five for folders, seven for card sets, and six for cards. We'll add one more in Section 8 for the copy feature, making it 22 total.

❒ Let's start with users. What endpoints do we need?

Three. POST slash users to register a new user. GET slash users to list all users. GET slash users slash user underscore id to get one specific user.

❒ Anything interesting in the user registration endpoint?

Yes — HTTP status code 409. Before inserting a new user, we check whether the username or email already exists in the database. If either does, we raise an HTTPException with status 409, which means Conflict. The request format is fine, but it conflicts with the current state — a user with that username already exists. We check explicitly so we can return a clear message like "Username already taken" instead of a raw database error.

❒ Now folders — those have ownership now, right?

Right. Five endpoints. POST to create a folder — the owner is whoever's making the request. GET slash my to get all folders you own. GET by folder ID to look up one specific folder. PUT to update a folder — owner only. DELETE to delete a folder — also owner only, and it cascades to card sets and cards. And here's something worth pointing out — the folder router follows the exact same ownership patterns as the card set router. Same helper functions, same verification steps, same error codes. That's a good sign. It means our design is consistent across entities.

❒ I noticed there's a verify underscore user helper function. What does that do?

It takes a user ID, queries the users table, and raises a 401 Unauthorized if the user doesn't exist. We call it at the start of any endpoint that needs a known user. This catches requests with fake or nonexistent user IDs before they go any further.

❒ And verify underscore folder underscore ownership?

Same pattern. Takes a folder ID and a user ID. Fetches the folder — if it doesn't exist, 404 Not Found. If it exists but the user underscore id doesn't match the requesting user, 403 Forbidden. The difference between 401 and 403 is important. 401 means "we don't know who you are" — that's an authentication failure. 403 means "we know who you are, but you're not allowed to do this" — that's an authorization failure.

❒ In the create folder endpoint, how does ownership get set?

Look at the line data bracket user underscore id equals x underscore user underscore id. The client sends the folder name and description in the body, but the owner is determined by the header. The client can't claim to create a folder on behalf of another user. Same pattern repeats for card sets.

❒ Let's move to card set endpoints. This is where multi-user features hit hardest?

Absolutely. Seven endpoints plus the copy we'll add later. The first is POST to create a card set. Before inserting, it does two things — verifies the requesting user exists, then verifies the parent folder exists and belongs to that user. You can't create a card set inside someone else's folder.

❒ What about the different GET endpoints for card sets?

There are four of them, and they handle visibility differently. GET slash my returns all card sets you own — no visibility filtering needed, you see everything that's yours. GET slash public returns all card sets where is underscore public is true — anyone can see these, no authentication needed.

❒ What about getting one specific card set?

That's GET by cardset underscore id, and here's where it gets interesting. The x-user-id header is optional — we use Header with default equals None instead of the ellipsis. Why optional? Because a public card set should be viewable by anyone, even anonymous users. But if the set is private, we check if the requester is the owner. If it's private and either they're not the owner or they didn't send a header at all — 403.

❒ And getting card sets within a specific folder?

That endpoint fetches all card sets in the folder, then filters in Python. It keeps sets that are either public or owned by the requesting user. We filter in Python because Supabase's chained query API doesn't easily support OR conditions like "where is underscore public equals true OR user underscore id equals this value." For small to medium datasets, filtering in Python is perfectly fine. If you're dealing with very large datasets, you could use a Supabase stored procedure or the dot or underscore filter method instead, but for our purposes this works great.

❒ Update and delete for card sets — both owner only?

Yes. Both call verify underscore user then verify underscore ownership. If either check fails, the endpoint stops. Only the owner can modify or delete their card sets. The update endpoint uses model underscore dump with exclude underscore unset equals True — that's crucial. It means only fields the client actually sent get included in the update. Without it, fields the client didn't mention would get sent as None, overwriting existing data in the database.

❒ Now cards — those inherit ownership from the parent card set?

Exactly. Cards don't have their own user underscore id column. Ownership is determined by the parent card set. So to check if someone can modify a card, we look up which card set the card belongs to, then check if that card set's owner matches the requesting user.

❒ How does that work in practice?

There's a helper called get underscore card underscore and underscore verify underscore ownership. It takes a card ID and a user ID. First it fetches the card — 404 if it doesn't exist. Then it calls verify underscore cardset underscore ownership with the card's cardset underscore id. Two database lookups chained together — find the card, find its card set, check the owner.

❒ The create card endpoint — how does that work?

The client sends a card with a cardset underscore id in the body. Before inserting, we verify the user exists and that they own that card set. This prevents User B from sneaking cards into User A's card set. Then there's the audio text auto-generation — if the client provides front text but not front audio text, we call generate underscore audio underscore text to create it automatically.

❒ What about reading cards — visibility comes into play there?

Yes. When someone asks for a specific card or all cards in a card set, we check the parent card set's is underscore public flag. If the set is private and the requester isn't the owner — 403. Visibility cascades. Making a card set private hides all its cards too. No need for per-card visibility flags.

❒ The update card endpoint — that's where the audit trail happens?

That's the big one. After assembling the update data and handling audio text regeneration, two critical lines run. First — data bracket updated underscore at equals datetime dot now with timezone dot utc, then dot isoformat. That sets the timestamp to the current moment in UTC, formatted as an ISO 8601 string — so it looks something like "2025-03-15T14:30:00+00:00." And by the way, both datetime and timezone come from Python's built-in datetime module — no extra packages needed. Second — data bracket updated underscore by equals x underscore user underscore id. That records who made the edit. Together they create a permanent record. For example: "This card was last modified on March 15, 2025 at 2:30 PM UTC by user abc-123." That's your audit trail, right there in the data.

❒ Why UTC specifically?

Consistency. If your server is in New York and mine is in Tokyo, datetime dot now without a timezone would give different results. Using timezone dot utc ensures every timestamp is in the same reference frame regardless of where the server runs.

❒ There's also an update history endpoint?

Yeah, endpoint 6 — GET slash cardset slash cardset underscore id slash updates. It returns a lightweight view of all cards in a set, showing only the identification fields and the audit fields. Think of it as a dashboard view — at a glance you can see which cards have been recently modified and by whom. The select call only asks for specific columns instead of everything.

❒ Can you give me the full count of endpoints across all routers?

Twenty-one total. Three user endpoints — register, list all, get one. Five folder endpoints — create, get mine, get one, update, delete. Seven card set endpoints — create, get mine, get public, get one, get by folder, update, delete. Six card endpoints — create, get one, get by card set, update, delete, and the update history view. We'll add one more in Section 8 for copying.

❒ Section 6 recap?

This is the heart of the app. The key patterns — Header with ellipsis for mandatory auth, Header with default None for optional auth. Status 401 for unknown users, 403 for known users who lack permission, 409 for conflicts like duplicate usernames. Helper functions encapsulate ownership checks so we don't repeat ourselves. Cards inherit visibility from their parent card set. Every card update stamps the audit trail. Six sections done, two to go.

---

---

## SECTION 7 — AUDIO TEXT GENERATION WITH REGULAR EXPRESSIONS

---

❒ Section 7 — audio text generation. What problem are we solving here?

Consider a flashcard for learning Spanish. The front might display: El gato, then in parentheses "the cat," then in square brackets "m dot" for masculine. That's great for reading — you see the word, the translation, the grammar note. But if you send that exact string to a text-to-speech engine, it would read "El gato open parenthesis the cat close parenthesis open bracket m period close bracket." That sounds terrible. What you want the TTS engine to say is just "El gato." Clean, natural speech.

❒ So we need a function that strips out all the visual formatting?

Exactly. We need to take display text and remove or transform things like parenthetical hints, square bracket annotations, and special notation. Regular expressions are perfect for this because they let us describe patterns rather than specific strings.

❒ How many transformation rules are we applying?

Five rules, applied in order. But before I go through them, let me quickly explain the tool we're using. The function is re dot sub, and it takes three arguments — the pattern you're looking for, what you want to replace it with, and the string you're searching in. So re dot sub pattern, replacement, string. It finds all occurrences of the pattern in the string and replaces each one with the replacement. Simple as that.

Alright, Rule 1 — remove anything in square brackets. The regex pattern backslash bracket dot star question mark backslash bracket matches an opening bracket, then any characters as few as possible, then a closing bracket. The replacement is just an empty string — we're deleting the match entirely. So "El gato bracket m dot bracket" becomes just "El gato."

❒ Why "as few as possible"? What does the question mark do?

That makes it non-greedy. Let me give you a concrete example. Imagine the text is "bracket one bracket word bracket two bracket" — so there are two separate bracketed sections with a word in between. A greedy pattern would match from the very first opening bracket all the way to the very last closing bracket, gobbling up everything in between — including that word you wanted to keep. Non-greedy matches each bracket pair individually — first it matches "bracket one bracket," then separately it matches "bracket two bracket." The word in between is preserved. Same thing applies to Rule 2 with parentheses. If you had "parenthesis one parenthesis word parenthesis two parenthesis," greedy would eat the whole thing, non-greedy handles each pair separately.

❒ Rule 2?

Same thing but for parentheses. Removes anything inside parentheses. So "El gato parenthesis the cat parenthesis" becomes "El gato."

❒ Rule 3?

Simplify slash alternatives. Sometimes a flashcard shows "rojo slash a" meaning the word can be rojo or roja. For audio we just want the first form — "rojo." The pattern captures a word before the slash using parentheses in the regex — that creates what's called a capture group. Then the replacement is backslash 1, written as r backslash 1 in Python. That r at the beginning makes it a raw string so the backslash doesn't get interpreted as an escape character. And backslash 1 simply means "put back whatever was in the first capture group." So the first word is kept, the slash and everything after it is dropped.

❒ Rule 4?

Remove leading numbers. If cards are numbered like "1 dot El gato," we strip the numbering for audio. The pattern matches digits followed by a dot at the start of the string.

❒ Rule 5?

Clean up whitespace. And this one has to come last — that's important. All those earlier rules, when they remove content, they leave behind gaps. A word that was between two bracketed sections now has a double space in the middle. So this final rule collapses multiple spaces into one and strips the edges. If you ran this rule earlier, you'd just end up with new gaps from the later rules.

❒ Can you walk through a complete example with all five rules?

Sure. Starting text: "3 dot El gato rojo slash a parenthesis the red cat parenthesis bracket m dot slash f dot bracket." After rule 1, the square bracket stuff is gone. After rule 2, the parenthetical stuff is gone. After rule 3, rojo slash a becomes just rojo. After rule 4, the "3 dot" numbering is gone. After rule 5, extra spaces collapse. Final result: "El gato rojo." Clean, natural, ready for text-to-speech.

❒ What if the user wants to provide their own audio text instead of the auto-generated one?

They can. If the client sends an explicit front underscore audio underscore text underscore 1 value in their request, the API uses that and skips the auto-generation. The function only kicks in when display text exists but audio text wasn't provided.

❒ How would I add my own custom rule later?

Just add another line in the function. Text equals re dot sub with your pattern, your replacement, and text. Put it in the right position in the sequence — you probably want cleanup rules at the end.

❒ Section 7 recap?

We built a generate underscore audio underscore text function that applies five regex rules — remove square brackets, remove parentheses, simplify slashes, remove numbering, clean whitespace. It gets called automatically in the card router when someone provides display text but not audio text. Seven sections done, one to go.

---

---

## SECTION 8 — PUBLIC SHARING AND THE COPY FEATURE

---

❒ Final section. Why do we need a copy feature?

Picture this. User A is a Spanish teacher who spent hours building a card set called DELE B2 Vocabulary with 200 perfectly crafted cards. Audio text, image URLs, the works. They mark it as public so their students can find it. Now User B, a student, discovers this set. They want to study from it, but they also want to add their own notes, tweak some translations, remove cards they already know. They can't edit the original — they're not the owner. And even if we let them, their changes would affect everyone else using the public set.

❒ So the solution is making a personal copy?

Exactly. User B creates a complete, independent duplicate. The copy belongs to them — they're the owner. They can edit, delete, add cards, make it private, whatever. User A's original is completely unaffected.

❒ What actually happens during a copy? It's not just copying one row, right?

No, it's multiple steps and the order matters. Step 1 — verify the source card set exists and is accessible. It either needs to be public or owned by the requester — you can copy your own sets too, which is useful for making variations. Step 2 — the user specifies which of their own folders to put the copy in, via a target underscore folder underscore id parameter. We verify that folder exists and belongs to them. Step 3 — create a new card set record with the target folder's ID, the source's name prefixed with "Copy of," and the requesting user as the owner. The copy starts private by default. Step 4 — fetch all cards from the source. Step 5 — duplicate each card into the new set.

❒ What gets copied and what doesn't?

All eight content fields are preserved exactly — front text, audio text, audio URL, image, same for back. And here's a small but important detail in how we read those fields — in the code, we use card dot get with the field name instead of card bracket field name. The difference? If a field doesn't exist or isn't populated, dot get just returns None gracefully. Bracket access would crash with a KeyError. It's defensive programming — handles edge cases where a card might not have every field filled in.

What does not get copied — the id, because each new card gets a fresh UUID. The cardset underscore id, because it points to the new set not the old one. The created underscore at, because it's set to right now by the database. And updated underscore at and updated underscore by are both null — the new card has never been edited, only created fresh.

❒ How does the endpoint look? What URL pattern?

POST slash cardsets slash cardset underscore id slash copy. The cardset underscore id in the URL is the source you want to copy. We use POST because this creates new data — it's not a read operation. The target underscore folder underscore id comes as a query parameter.

❒ Is there a performance trick for copying lots of cards?

Yes — batch insert. Instead of inserting cards one at a time in a loop, which would make one database call per card, we collect all the new cards in a list and call insert once with the entire list. Supabase's insert method accepts a list of dictionaries. So copying 200 cards is one network call instead of 200. Dramatically faster.

❒ What does the endpoint return?

The new card set record. The client now has the ID of their copy and can use the get cards by card set endpoint to see all the copied cards.

❒ Can you walk through a full test scenario?

Sure, let's walk through the whole thing step by step. First, register two users using POST slash users. Teacher underscore ana with their email, and student underscore bob with theirs. Copy both user IDs from the responses.

Next, the teacher creates a folder. POST slash cardfolders with the x-user-id header set to the teacher's ID and the body has the name "Languages." Copy the folder ID. The student does the same — creates their own folder called "My Studies" with their own user ID in the header. Copy that folder ID too — the student will need it for the copy later.

Now the teacher creates a card set. POST slash cardsets, header is the teacher's ID, body has the cardfolder underscore id pointing to the teacher's Languages folder, name is "Spanish Basics," and is underscore public is set to true. Copy the card set ID.

The teacher adds some cards. POST slash cards with the teacher's header, and a body like cardset underscore id set to that card set, front underscore text underscore 1 set to "El gato parenthesis the cat parenthesis bracket m dot bracket," back underscore text underscore 1 set to "The cat." Do this a few times. And notice in the response — front underscore audio underscore text underscore 1 automatically shows up as just "El gato." The regex cleaned it up.

Now the student browses. GET slash cardsets slash public — no header needed. They see Spanish Basics listed right there.

The student copies it. POST slash cardsets slash the card set ID slash copy, with the query parameter target underscore folder underscore id set to the student's "My Studies" folder ID, and the x-user-id header set to the student's ID. Response comes back — a new card set called "Copy of Spanish Basics," owned by the student, private by default, inside their folder.

The student checks their collection. GET slash cardsets slash my with their header. "Copy of Spanish Basics" is right there.

Now the fun part — the student edits a card in their copy. First GET slash cards slash cardset slash the new card set ID to see all the copied cards. Pick one card ID. Then PUT slash cards slash that card ID with the student's header and body like front underscore text underscore 1 set to "El gato gordo parenthesis the fat cat parenthesis." In the response, updated underscore at shows the current timestamp, updated underscore by shows the student's ID, and front underscore audio underscore text underscore 1 automatically regenerated as "El gato gordo." The audit trail is live.

Then verify the teacher's original is untouched. GET slash cards slash cardset slash the original card set ID. Everything is exactly as the teacher left it. The student's edits only touched their copy.

And finally — the student tries to edit the teacher's original card. PUT slash cards slash the teacher's card ID, with the student's header. Boom — 403 Forbidden, "You do not own the parent card set." The ownership system works.

❒ Section 8 recap?

The copy endpoint performs a deep copy — new card set plus all cards duplicated. Content preserved exactly, metadata starts fresh. Only public sets or your own sets can be copied. Target folder must belong to you. Batch insert for efficiency. All eight sections are now complete.

---

---

## FINAL SUMMARY

---

❒ We've been through all eight sections. Can you give us the complete picture?

Thirteen files created. Dot env and dot gitignore for credentials and protection. Database dot py for the Supabase connection. Main dot py as the entry point with four router includes. Four model files for data validation. Four router files for endpoint logic. And audio underscore text dot py for the regex-based audio text generator. Twenty-two endpoints total plus a root health check.

❒ What multi-user features did we implement?

User registration and lookup. Folder ownership. Card set ownership. Ownership enforcement on every single write operation. Public and private visibility through the is underscore public flag. Visibility filtering on all read operations. Card-level audit trail through updated underscore at and updated underscore by. Deep copy of public card sets with batch card duplication. And simplified authentication through the x-user-id header.

❒ How do you actually run this thing?

Three commands. cd flashcard-api. workon vintel. uvicorn main colon app dash dash reload. Then open localhost colon 8000 slash docs in your browser and you can see and test every endpoint interactively.

❒ If someone only remembers a few things from this whole tutorial, what should they be?

Four things. One — the data hierarchy is users, folders, card sets, cards. Ownership flows down, visibility is controlled at the card set level. Two — ON DELETE CASCADE means deleting a parent deletes its children. ON DELETE SET NULL means clearing a reference without destroying data. Three — the API, not the client, controls audit trail fields. Updated underscore at and updated underscore by are set automatically, never by the request body. And four — the copy feature does a deep copy. Content is preserved exactly, but IDs, timestamps, and audit fields all start fresh. The copy is completely independent from the original.

❒ And that's a wrap?

That's a wrap. You've got a fully functional, multi-user flashcard API built from scratch with FastAPI and Supabase.
