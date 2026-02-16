# Building a Flashcard API from Zero: A Complete FastAPI + Supabase Tutorial

---

## MASTER OVERVIEW — What We Are Building and How This Tutorial Is Organized

Before we write a single line of code, let us get a complete birds-eye view of what we are going to build and the exact sequence of steps we will follow. This tutorial is divided into **eight sections**, and here they are:

**Section 1 — Why FastAPI and What Problem Does It Solve.** We understand what an API is, why you cannot just use plain Python scripts to serve data, and why FastAPI is the tool we choose. We also introduce the multi-user problem — why an API that serves flashcards to multiple users needs ownership, privacy, and audit trails.

**Section 2 — Environment Setup on macOS.** We install everything: Python, FastAPI, the Supabase client, and we create the folder structure for our project. This is entirely practical, command-by-command.

**Section 3 — Database Design in Supabase.** We design four tables — `users`, `cardfolders`, `cardsets`, `cards` — and we understand how foreign keys connect them. We build these tables directly in the Supabase dashboard. Crucially, both `cardfolders` and `cardsets` will carry a `user_id` (ownership), `cardsets` will additionally carry an `is_public` flag (visibility), and `cards` will carry `updated_at` and `updated_by` fields for full edit audit trails.

**Section 4 — Project Architecture.** We create the actual files and folders on our machine. We understand what a "router" is in FastAPI, why we split our code into multiple files, and how the main application file ties everything together — now including a user router.

**Section 5 — Pydantic Models.** We build the validation layer. Every piece of data that enters or leaves our API gets checked by Pydantic models. We create models for users, folders, cardsets (with ownership and visibility), and cards (with update tracking).

**Section 6 — Building Every Endpoint.** This is the longest section. We write every single CRUD endpoint for all entities. We cover path parameters, query logic, error handling, ownership enforcement (only the owner of a card set can edit it), and the relationship between parent and child entities.

**Section 7 — Audio Text Generation with Regular Expressions.** We build the system that automatically generates "audio-friendly" text from the display text on each card.

**Section 8 — Public Sharing and the Copy Feature.** We build the system that lets users browse public card sets created by other users, and copy an entire public card set into their own collection with a single API call.

That is the full roadmap. Eight sections. Now let us begin.

---

---

## SECTION 1 — WHY FASTAPI AND WHAT PROBLEM DOES IT SOLVE

---

### 1.1 — The Core Problem: How Do You Serve Data to an Application?

Imagine you have written a simple Python script. It reads a JSON file, processes some flashcard data, and prints results to the terminal. That works fine when you are the only person using it, and you are sitting at your own computer. But what happens when you want a phone app, a web browser, or another program on a different machine to access that same flashcard data? Your Python script has no way to listen for incoming requests. It runs once and stops. There is no door for the outside world to knock on.

You might think: well, I could put the JSON file on a web server and let the app download it. Yes, but then you lose the ability to create new cards, update existing ones, or delete them from the app. A static file is read-only. You need a living, breathing program that sits on a server, waits for requests, processes them, talks to a database, and sends back responses. That living program is called an **API** — an Application Programming Interface.

An API is a program that exposes a set of **endpoints**. An endpoint is a specific URL — like `http://localhost:8000/cardfolders` — that, when accessed with the right HTTP method (GET, POST, PUT, DELETE), performs a specific action. GET retrieves data. POST creates new data. PUT updates existing data. DELETE removes data. These four operations are called **CRUD** — Create, Read, Update, Delete — and they map directly to the four HTTP methods we just listed.

### 1.2 — Why FastAPI Specifically?

Python has several frameworks for building APIs. Flask is the most well-known. Django REST Framework is another. So why FastAPI?

Three reasons matter for us:

**First, automatic data validation.** When someone sends data to your API — say, a new flashcard — you need to check that data before putting it in your database. Is the front text actually a string? Is the image URL a valid URL? In Flask, you would write all this validation code manually. FastAPI uses a library called **Pydantic** to handle this automatically. You define a model that says "front_text_1 must be a string, front_image must be an optional string," and FastAPI rejects any request that does not match before your code even runs.

**Second, automatic documentation.** The moment you start your FastAPI server, it generates an interactive web page at `http://localhost:8000/docs` where you can see every endpoint, what data it expects, and you can test each endpoint directly from your browser. You do not need Postman or curl. This is invaluable for learning and debugging.

**Third, speed and modern Python.** FastAPI uses Python type hints natively. If you write `front_text_1: str` in your function, FastAPI uses that type hint both for validation and for documentation. The framework is also asynchronous-capable, meaning it can handle many requests simultaneously without blocking — though for our tutorial we will use synchronous code because it is simpler to learn.

### 1.3 — What Is Supabase and Why Not Just a Local Database?

Supabase is a hosted PostgreSQL database with a web dashboard and a Python client library. You create your tables in a web interface, and then from your Python code, you call functions like `supabase.table("cards").select("*").execute()` to read data.

Why not just use a local SQLite file? You could, and for a personal learning project it would work. But Supabase gives us three advantages: the database is accessible from anywhere (not just your laptop), it has a visual dashboard where you can see your data in real time, and its Python client library is clean and straightforward. When you later deploy your API to a server, the Supabase connection works identically — no migration required.

### 1.4 — The Multi-User Problem: Ownership, Privacy, and Audit Trails

Now imagine your flashcard API is not just for you — it serves many users. This introduces three problems that a single-user system never has to deal with:

**Problem one: ownership.** If User A creates a card set called "Spanish Verbs," User B should not be able to edit or delete it. Every card set needs an owner, and every write operation (create, update, delete) must check whether the requesting user is actually the owner. Without ownership, any user can destroy any other user's work.

**Problem two: visibility.** Maybe User A wants to keep their card set private — only they can see it. But maybe User A also has a fantastic set called "JLPT N5 Kanji" that they want to share with the world. We need a flag on each card set — `is_public` — that controls whether other users can see it. Private sets are invisible to everyone except the owner. Public sets are browsable by all.

**Problem three: audit trails.** When a card is updated, you want to know when it was updated and who updated it. This is essential in any multi-user system. If something goes wrong — a card's text gets corrupted, or someone makes an accidental edit — you need a trail showing the last modification timestamp and the user responsible. Every card will carry `updated_at` and `updated_by` fields.

There is also a fourth feature that naturally follows from public visibility: **copying.** If User B sees User A's public card set and wants their own copy (so they can modify it, add cards, track their own progress), the API should support a one-click copy operation that duplicates the entire card set and all its cards into User B's account.

These four features — ownership, visibility, audit trails, and copying — turn our flashcard API from a single-user toy into a genuine multi-user platform. They will be woven into every section of this tutorial.

### Section 1 — Review

Let us pause and review what we have established. We need an API because static files cannot handle CRUD operations from external applications. We chose FastAPI because it gives us automatic validation via Pydantic, automatic documentation, and modern Python type hints. We chose Supabase because it gives us a hosted PostgreSQL database with a visual dashboard and a clean Python client. We introduced the multi-user problem: ownership (who can edit), visibility (public vs. private), audit trails (who changed what and when), and copying (duplicating public sets). We have eight sections ahead of us. Section 1 is now complete. Let us move to Section 2 — setting up our environment.

### Section 1 — Q&A Table

| # | Question | Answer |
|---|----------|--------|
| 1 | What does API stand for? | Application Programming Interface — a program that listens for HTTP requests and responds with data or actions. |
| 2 | What are the four CRUD operations and their HTTP methods? | Create = POST, Read = GET, Update = PUT, Delete = DELETE. |
| 3 | Why can't a plain Python script serve as an API? | It runs once and exits. It has no mechanism to listen for incoming HTTP requests from other applications. |
| 4 | What is Pydantic? | A Python library for data validation. You define a model with typed fields, and it automatically checks that incoming data matches those types. |
| 5 | Why does FastAPI generate documentation automatically? | It reads your Python type hints and Pydantic models and uses them to build an interactive Swagger UI page at the /docs endpoint. |
| 6 | What is Supabase? | A hosted PostgreSQL database service with a web dashboard and client libraries for Python, JavaScript, and others. |
| 7 | Why do we need ownership on card sets? | To prevent User B from editing or deleting card sets that belong to User A. Every write operation must verify the requester is the owner. |
| 8 | What does `is_public` control? | Whether a card set is visible to users other than its owner. Private sets are hidden from everyone except the owner. |
| 9 | Why track `updated_at` and `updated_by` on cards? | To create an audit trail — knowing when a card was last modified and by whom helps diagnose issues and maintain accountability. |
| 10 | What is the copy feature? | The ability for any user to duplicate an entire public card set (with all its cards) into their own account, becoming the owner of the copy. |

---

---

## SECTION 2 — ENVIRONMENT SETUP ON macOS

---

We are now in Section 2. Remember our roadmap: Section 1 explained why we need FastAPI and Supabase (essentially, we need a living program that handles CRUD operations and talks to a database for multiple users). Now in Section 2, we install everything and create our project skeleton. After this section, you will have a working folder on your Mac with all dependencies installed and ready to go.

There are **four steps** in this section:
1. Create a project folder and a Python virtual environment
2. Install FastAPI, Uvicorn, and the Supabase client
3. Create a `.env` file for your Supabase credentials
4. Verify everything works with a test run

Let us go through each one.

### 2.1 — Step 1: Create the Project Folder and Virtual Environment

**Concrete layer — what you type:**

Open your Terminal on macOS. Type the following commands one at a time:

```bash
mkdir flashcard-api
cd flashcard-api
python3 -m venv venv
source venv/bin/activate
```

After running these four commands, your terminal prompt will change. It will now show `(venv)` at the beginning, which means you are inside the virtual environment.

**Abstract layer — what just happened:**

The first command, `mkdir flashcard-api`, creates an empty directory called `flashcard-api`. The second command, `cd flashcard-api`, moves us into that directory. The third command, `python3 -m venv venv`, creates a virtual environment inside a subfolder called `venv`. And the fourth command, `source venv/bin/activate`, activates that virtual environment.

A virtual environment is an isolated Python installation inside your project. When you install libraries while the virtual environment is active, they go into the `venv` folder, not into your system Python. This means your flashcard project's dependencies will never conflict with another project's dependencies. Every time you open a new terminal window to work on this project, you must run `source venv/bin/activate` again — the activation does not persist between terminal sessions.

### 2.2 — Step 2: Install FastAPI, Uvicorn, and the Supabase Client

**Concrete layer — what you type:**

With your virtual environment active (you should see `(venv)` in your prompt), run:

```bash
pip install fastapi uvicorn supabase python-dotenv
```

This single command installs four packages. Let us understand each one.

**Abstract layer — what each package does:**

`fastapi` is the web framework itself. It provides the decorators like `@app.get()` and `@app.post()` that turn your Python functions into API endpoints.

`uvicorn` is the server that actually runs your FastAPI application. FastAPI by itself is just a set of rules and decorators — it cannot listen for HTTP requests on its own. Uvicorn is the engine that listens on a port (port 8000 by default), receives incoming HTTP requests, hands them to FastAPI for processing, and sends the responses back.

`supabase` is the official Python client library for Supabase. It provides a `create_client` function that creates a connection object, and then you use that object to call methods like `.table("cards").select("*").execute()` to interact with your database.

`python-dotenv` is a small utility that reads a file called `.env` from your project directory and loads its contents as environment variables. This is how we keep our Supabase URL and API key out of our source code — we put them in `.env`, which we never commit to version control.

### 2.3 — Step 3: Create the .env File

**Concrete layer — what you create:**

In the root of your `flashcard-api` folder, create a file called `.env` (notice the dot at the beginning — this makes it a hidden file on macOS). The contents should be:

```
SUPABASE_URL=https://your-project-id.supabase.co
SUPABASE_KEY=your-anon-key-here
```

To find these values, go to your Supabase dashboard at `https://supabase.com`, open your project, click on **Project Settings** in the left sidebar, then click **API**. You will see two values: the **Project URL** and the **anon public** key. Copy them into your `.env` file.

**Abstract layer — why we do this:**

Your Supabase URL and API key are credentials. If you hardcode them directly in your Python files and then push your code to GitHub, anyone can see them and access your database. The `.env` file is a convention in software development: you store secrets in this file, and you add `.env` to your `.gitignore` file so it never gets committed. The `python-dotenv` library reads this file at runtime and makes those values available via `os.environ["SUPABASE_URL"]`.

Also create a `.gitignore` file in the root of your project:

```
venv/
.env
__pycache__/
```

This tells Git to ignore your virtual environment folder, your secrets file, and Python's cache files.

### 2.4 — Step 4: Verify Everything Works

**Concrete layer — what you type:**

Create a file called `test_setup.py` in your project root with this content:

```python
from fastapi import FastAPI

app = FastAPI()

@app.get("/")
def root():
    return {"message": "Flashcard API is alive"}
```

Now run:

```bash
uvicorn test_setup:app --reload
```

Open your browser and go to `http://localhost:8000`. You should see `{"message": "Flashcard API is alive"}`. Then go to `http://localhost:8000/docs` and you should see the interactive Swagger documentation with one endpoint listed.

**Abstract layer — what just happened:**

The command `uvicorn test_setup:app --reload` tells Uvicorn to look inside the file `test_setup.py` for an object called `app`, and to start serving it. The `--reload` flag means Uvicorn will watch your files for changes and automatically restart the server when you save a file — extremely useful during development.

Inside `test_setup.py`, we import `FastAPI` from the `fastapi` package, create an instance called `app`, and use the decorator `@app.get("/")` to register a function called `root` as the handler for GET requests to the path `/`. When someone accesses `http://localhost:8000/`, FastAPI calls the `root` function and returns its dictionary as a JSON response.

Press `Ctrl+C` in your terminal to stop the server. You can delete `test_setup.py` now — it was only for verification.

### Section 2 — Review

Let us review Section 2. We did four things. First, we created the project folder and a virtual environment with `python3 -m venv venv` and activated it with `source venv/bin/activate`. Second, we installed four packages: `fastapi` (the framework), `uvicorn` (the server), `supabase` (the database client), and `python-dotenv` (for reading the `.env` file). Third, we created a `.env` file containing our Supabase URL and key, and a `.gitignore` to protect those secrets. Fourth, we verified everything by creating a tiny test file and running Uvicorn.

Our project folder currently looks like this:

```
flashcard-api/
├── .env
├── .gitignore
└── venv/
```

That is all we need so far. Section 2 is done. Now we move to Section 3, where we design our database tables in Supabase — including the new `users` table and the ownership, visibility, and audit columns.

### Section 2 — Q&A Table

| # | Question | Answer |
|---|----------|--------|
| 1 | What command creates a virtual environment? | `python3 -m venv venv` — this creates a folder called `venv` with an isolated Python installation. |
| 2 | Why must you activate the virtual environment every time? | Activation is session-specific. Each new terminal window starts without it. Run `source venv/bin/activate`. |
| 3 | What does Uvicorn do? | It is the ASGI server that listens for HTTP requests and passes them to FastAPI. FastAPI alone cannot receive requests. |
| 4 | What does `python-dotenv` do? | It reads the `.env` file and loads its key-value pairs as environment variables accessible via `os.environ`. |
| 5 | What does the `--reload` flag do in Uvicorn? | It watches your source files and automatically restarts the server when you save changes. |
| 6 | What format does `uvicorn test_setup:app` expect? | `filename_without_extension:variable_name` — it looks for the `app` object inside `test_setup.py`. |
| 7 | Why should `.env` be in `.gitignore`? | It contains your Supabase credentials. Committing it to Git would expose your database to anyone who can see the repo. |
| 8 | Where do you find your Supabase URL and key? | In the Supabase dashboard → Project Settings → API. The URL and the "anon public" key. |

---

---

## SECTION 3 — DATABASE DESIGN IN SUPABASE

---

We are now in Section 3. Quick recap of where we stand: Section 1 explained why we need an API, a database, and multi-user features (ownership, visibility, audit trails, copying). Section 2 set up our development environment — we have FastAPI, Uvicorn, Supabase client, and python-dotenv installed, a virtual environment, and a `.env` file with our credentials. Now in Section 3, we design the actual database tables.

This section has **four parts**:
1. Understanding the data hierarchy (users → folders → cardsets → cards)
2. Understanding why we normalize into multiple tables instead of one
3. Understanding the new multi-user columns (ownership, visibility, audit)
4. Creating the four tables in Supabase

### 3.1 — Understanding the Data Hierarchy

Our flashcard system has four levels of entities:

At the foundation, we have **users**. A user is a person who registers with our system. Every user has a unique ID, a username, and an email. Users own folders and card sets.

Next, we have **card folders**. A card folder is a container — it groups related collections of cards. For example, a folder called "Spanish Vocabulary" or "Medical Terms." **Each folder is owned by exactly one user.** User A's "Spanish Vocabulary" folder is entirely separate from User B's "Spanish Vocabulary" folder. Each user organizes their own folders however they like.

Inside each folder, we have **card sets**. A card set is a specific collection of flashcards within that folder. The folder "Spanish Vocabulary" might contain card sets like "Food Words," "Colors," and "Verbs." **Each card set is also owned by exactly one user** — the same user who owns the parent folder. Additionally, each card set has an `is_public` flag: if true, anyone can view it and copy it. If false, only the owner can see it. Note that visibility is controlled at the card set level, not the folder level — this keeps the logic simple and avoids contradictions (like a public card set inside a private folder).

Inside each card set, we have **cards**. Each card has a front and a back. The front has four fields: a display text, an audio text, an audio file URL, and an image URL. The back has the exact same four fields. Each card also carries `updated_at` (when it was last modified) and `updated_by` (which user made the last modification). These two fields create the audit trail we discussed in Section 1.

The relationships: a user owns many folders. A folder belongs to exactly one user and contains many card sets. A card set belongs to exactly one folder and is owned by the same user who owns the folder. A card set contains many cards. A card belongs to exactly one card set.

### 3.2 — Why Multiple Tables Instead of One Giant Table?

You might ask: why not put everything in a single table? You could have one row per card, and each row includes columns for the folder name, card set name, owner name, and so on. It would work, technically. But it creates serious problems.

**Problem one: data duplication.** If a folder called "Spanish Vocabulary" contains 500 cards across 10 card sets, the string "Spanish Vocabulary" appears 500 times in the table. If you want to rename the folder, you need to update 500 rows instead of one.

**Problem two: deletion anomalies.** If you delete all cards in a card set, the card set itself vanishes — there is no row left to remember it existed. But maybe you wanted to keep the empty card set as a placeholder for future cards.

**Problem three: inconsistency risk.** If one row says the folder is "Spanish Vocabulary" and another says "Spanish Vocabulay" (a typo), you have conflicting data with no way to know which is correct.

**Problem four: user data duplication.** Without a separate users table, every card would repeat the user's name, email, and other data. If a user changes their email, you would need to update every card they ever touched.

The solution is **normalization** — splitting data into separate tables where each fact is stored exactly once. The folder name is stored once in the `cardfolders` table. The user's data is stored once in the `users` table. Each card set stores a reference (a foreign key) pointing to which folder and which user it belongs to.

### 3.3 — Understanding the Multi-User Columns

Before we create the tables, let us understand the three categories of new columns that the multi-user features require:

**Category 1: Ownership columns.** Both the `cardfolders` and `cardsets` tables get a `user_id` column — a foreign key pointing to the `users` table. This answers the question: "Who owns this folder?" and "Who owns this card set?" Every write operation on a folder or card set (update, delete, adding children) will check this column against the requesting user's ID. If they do not match, the API returns a 403 Forbidden error.

**Category 2: Visibility columns.** The `cardsets` table gets an `is_public` column — a boolean that defaults to `false`. When a user creates a card set, it is private by default. They can later flip it to public if they want to share. When another user queries for card sets, the API will filter: show all their own sets plus any set where `is_public` is true.

**Category 3: Audit columns.** The `cards` table gets two new columns: `updated_at` (a timestamp, initially null, set every time the card is modified) and `updated_by` (a UUID pointing to the user who made the modification). These are separate from `created_at` because a card might be created by one user (the owner of the card set) but hypothetically edited by an API admin or batch process. In our system, only the owner can edit, but the columns are designed for future flexibility.

### 3.4 — Creating the Four Tables in Supabase

We will create four tables. Go to your Supabase dashboard, click **Table Editor** in the left sidebar, and create each table in the order listed (order matters because foreign keys reference tables that must already exist).

**Table 1: `users`** (create this first — other tables reference it)

| Column Name | Type | Constraints |
|-------------|------|-------------|
| `id` | `uuid` | Primary Key, default: `gen_random_uuid()` |
| `username` | `text` | NOT NULL, UNIQUE |
| `email` | `text` | NOT NULL, UNIQUE |
| `created_at` | `timestamptz` | default: `now()` |

This is the user identity table. Each user has a unique ID, a unique username, and a unique email. The `UNIQUE` constraints on `username` and `email` mean the database itself will reject any attempt to register a duplicate username or email — this is enforced at the database level, not just in our Python code.

In Supabase: click "New Table", name it `users`. Uncheck "Enable Row Level Security" for now (we will worry about security later). Add each column as listed. For the `username` and `email` columns, after creating them, go to the column settings and check "Is Unique."

**Table 2: `cardfolders`** (create this second — it references `users`)

| Column Name | Type | Constraints |
|-------------|------|-------------|
| `id` | `uuid` | Primary Key, default: `gen_random_uuid()` |
| `user_id` | `uuid` | NOT NULL, Foreign Key → `users.id` ON DELETE CASCADE |
| `name` | `text` | NOT NULL |
| `description` | `text` | Nullable |
| `created_at` | `timestamptz` | default: `now()` |

Each folder has a unique ID, an owner (`user_id`), a name, an optional description, and a creation timestamp. The `user_id` column references `users.id` with `ON DELETE CASCADE` — if a user deletes their account, all their folders (and consequently all their card sets and cards within those folders) are deleted too.

In Supabase: click "New Table", name it `cardfolders`. Uncheck "Enable Row Level Security" for now. Add the `user_id` column with type `uuid`, click the link icon and set it to reference `users.id` with cascade delete.

**Table 3: `cardsets`** (create this third — it references both `users` and `cardfolders`)

| Column Name | Type | Constraints |
|-------------|------|-------------|
| `id` | `uuid` | Primary Key, default: `gen_random_uuid()` |
| `cardfolder_id` | `uuid` | NOT NULL, Foreign Key → `cardfolders.id` ON DELETE CASCADE |
| `user_id` | `uuid` | NOT NULL, Foreign Key → `users.id` ON DELETE CASCADE |
| `name` | `text` | NOT NULL |
| `description` | `text` | Nullable |
| `is_public` | `boolean` | NOT NULL, default: `false` |
| `created_at` | `timestamptz` | default: `now()` |

This table has three foreign keys worth discussing:

The column `cardfolder_id` references `cardfolders.id`. This means every card set must belong to an existing folder. The `ON DELETE CASCADE` clause means that if you delete a folder, all card sets in it are automatically deleted too.

The column `user_id` references `users.id`. This is the **ownership** link. Every card set belongs to exactly one user. The `ON DELETE CASCADE` here means if a user account is deleted, all their card sets (and consequently all their cards, via the next cascade) are deleted too. This prevents orphaned data — card sets pointing to a user that no longer exists.

The column `is_public` is a boolean defaulting to `false`. When a card set is first created, it is private. The owner can later update it to `true` to share it publicly. Our API endpoints will use this column to filter what non-owners can see.

In Supabase: create the table, add the `cardfolder_id` column with type `uuid`, click the link icon and set it to reference `cardfolders.id` with cascade delete. Do the same for `user_id`, referencing `users.id` with cascade delete. For `is_public`, select type `bool` and set default value to `false`.

**Table 4: `cards`** (create this last — it references `cardsets` and `users`)

| Column Name | Type | Constraints |
|-------------|------|-------------|
| `id` | `uuid` | Primary Key, default: `gen_random_uuid()` |
| `cardset_id` | `uuid` | NOT NULL, Foreign Key → `cardsets.id` ON DELETE CASCADE |
| `front_text_1` | `text` | Nullable |
| `front_audio_text_1` | `text` | Nullable |
| `front_audio_1` | `text` | Nullable |
| `front_image` | `text` | Nullable |
| `back_text_1` | `text` | Nullable |
| `back_audio_text_1` | `text` | Nullable |
| `back_audio_1` | `text` | Nullable |
| `back_image` | `text` | Nullable |
| `created_at` | `timestamptz` | default: `now()` |
| `updated_at` | `timestamptz` | Nullable, no default |
| `updated_by` | `uuid` | Nullable, Foreign Key → `users.id` ON DELETE SET NULL |

Let us walk through every column, starting with the ones that are new compared to a single-user system.

The eight content fields (`front_text_1` through `back_image`) are identical to what we described in Section 1: display text, audio text, audio URL, and image URL for both front and back. All nullable because a card might only have some of these populated.

The field `created_at` is auto-set to the current timestamp when the card is first inserted. It never changes after that.

The field `updated_at` starts as null (the card has never been updated — only created). Every time someone updates this card, our API will set `updated_at` to the current timestamp. This tells you exactly when the most recent edit happened.

The field `updated_by` also starts as null. Every time someone updates this card, our API will set `updated_by` to the user ID of the person who made the edit. Notice the foreign key constraint is `ON DELETE SET NULL`, not `ON DELETE CASCADE`. Why? Because if the user who last edited a card is later deleted from the system, we do not want to delete the card itself — that would be data loss. Instead, we set `updated_by` to null, which means "the user who last edited this card no longer exists in the system." The card data is preserved; only the audit reference is cleared.

This is a different cascade strategy than we used for `cardset_id` (where deleting a card set SHOULD delete its cards, because cards cannot exist without a card set). The choice of cascade behavior depends on the relationship: "this entity cannot exist without its parent" → CASCADE. "This is a reference for informational purposes" → SET NULL.

### 3.5 — The Complete Relationship Diagram

Here is how the four tables relate:

```
users (1) ──────< (many) cardfolders (1) ──────< (many) cardsets (1) ──────< (many) cards
  id   ◄──── user_id          id      ◄──── cardfolder_id    id    ◄──── cardset_id
  username    name             user_id ◄──── user_id          name
  email       description     name              is_public
                               description

users (1) ─ ─ ─ ─< (many) cards
  id   ◄ ─ ─ ─  updated_by   (SET NULL on delete, not CASCADE)
```

A user can own many folders. A folder can contain many card sets. A card set belongs to one user and one folder. A card set contains many cards. If a user is deleted, their folders cascade-delete, which cascade-deletes their card sets, which cascade-deletes their cards. If a user is deleted but they only edited (not owned) a card, that card survives with `updated_by` set to null.

### Section 3 — Review

Let us review Section 3. We have four tables: `users` (identity), `cardfolders` (owned by a user, organizing card sets), `cardsets` (owned by a user, optionally public, within a folder), and `cards` (the actual data, with update audit fields). Normalization prevents data duplication. Foreign keys with CASCADE enforce that deleting a parent removes its children — deleting a user cascades through folders, card sets, and cards. The `is_public` boolean on `cardsets` controls visibility (not on folders — visibility is managed at the card set level only). The `updated_at` and `updated_by` columns on `cards` provide an edit audit trail. We use `ON DELETE SET NULL` for the `updated_by` reference because we want to preserve cards even if the editing user is deleted.

Three out of eight sections are complete. Next is Section 4, where we create the actual project file structure.

### Section 3 — Q&A Table

| # | Question | Answer |
|---|----------|--------|
| 1 | How many tables do we create? | Four: `users`, `cardfolders`, `cardsets`, and `cards`. |
| 2 | What is a foreign key? | A column in one table that references the primary key of another table, establishing a parent-child relationship. |
| 3 | What does ON DELETE CASCADE mean? | When the parent row is deleted, all child rows referencing it are automatically deleted too. |
| 4 | What does ON DELETE SET NULL mean? | When the referenced row is deleted, the foreign key column is set to null instead of deleting the referencing row. |
| 5 | Why does `updated_by` use SET NULL instead of CASCADE? | Because deleting a user who edited a card should not delete the card itself — only the audit reference is cleared. |
| 6 | What does `is_public` default to? | `false` — all new card sets are private by default. The owner must explicitly make them public. |
| 7 | Do folders have a `user_id`? | Yes — every folder is owned by the user who created it. Deleting a user cascades through their folders, card sets, and cards. |
| 8 | What ensures usernames and emails are unique? | UNIQUE constraints on the `username` and `email` columns in the `users` table, enforced at the database level. |
| 9 | Why is `updated_at` initially null? | A brand-new card has been created but never updated. Null clearly communicates "no edits have occurred yet." |
| 10 | What happens when a user deletes their account? | CASCADE: all their folders are deleted, all card sets in those folders are deleted, and all cards in those sets are deleted. SET NULL: any `updated_by` references to them become null. |

---

---

## SECTION 4 — PROJECT ARCHITECTURE

---

We are now in Section 4. Recap: Section 1 gave us the "why" — we need a multi-user API with ownership, visibility, audit trails, and copying. Section 2 gave us the tools — everything installed and verified. Section 3 gave us the database — four tables with foreign keys, cascade strategies, and multi-user columns. Now, Section 4 gives us the project structure — the files and folders on our machine that organize our code.

This section has **three parts**:
1. Why we split code into multiple files (routers)
2. The complete folder and file structure
3. The two foundational files: `database.py` and `main.py`

### 4.1 — Why Split Code Into Multiple Files?

If you put every endpoint in one file, that file will become enormous. We will have CRUD operations for users, folders, cardsets, and cards, plus ownership checks, visibility filters, and the copy feature — that is well over 20 endpoints. A single file with 20+ endpoint functions, plus imports, plus helper logic, becomes unreadable very quickly.

FastAPI solves this with **routers**. A router is a mini-application that handles a subset of endpoints. You create one router for user endpoints, one for folder endpoints, one for cardset endpoints, and one for card endpoints. Each router lives in its own file. Then, in your main application file, you "include" all routers. The `APIRouter` class from FastAPI works identically to the `FastAPI` app class in terms of decorators. Instead of writing `@app.get("/cardfolders")`, you write `@router.get("/cardfolders")`. The difference is that a router is not a standalone application — it needs to be included into the main `FastAPI()` app via `app.include_router(router)`.

### 4.2 — The Complete Folder and File Structure

**Concrete layer — what you create on disk:**

Here is the exact structure. Create these folders and files now:

```
flashcard-api/
├── .env
├── .gitignore
├── main.py
├── database.py
├── models/
│   ├── __init__.py
│   ├── user_models.py
│   ├── cardfolder_models.py
│   ├── cardset_models.py
│   └── card_models.py
├── routers/
│   ├── __init__.py
│   ├── user_router.py
│   ├── cardfolder_router.py
│   ├── cardset_router.py
│   └── card_router.py
├── utils/
│   ├── __init__.py
│   └── audio_text.py
└── venv/
```

To create this structure from your terminal (make sure you are in the `flashcard-api` directory):

```bash
mkdir models routers utils
touch main.py database.py
touch models/__init__.py models/user_models.py models/cardfolder_models.py models/cardset_models.py models/card_models.py
touch routers/__init__.py routers/user_router.py routers/cardfolder_router.py routers/cardset_router.py routers/card_router.py
touch utils/__init__.py utils/audio_text.py
```

**Abstract layer — what each piece does:**

`main.py` is the entry point. It creates the `FastAPI()` application object, includes all four routers (users, folders, cardsets, cards), and that is all. Uvicorn runs this file.

`database.py` establishes the connection to Supabase. It reads the `.env` file, creates a Supabase client object, and exports it for all other files to use.

The `models/` folder contains Pydantic models. `user_models.py` defines the shape of user data. `cardfolder_models.py` defines folder data. `cardset_models.py` defines card set data including `user_id` and `is_public`. `card_models.py` defines card data including `updated_at` and `updated_by`.

The `routers/` folder contains the endpoint logic. `user_router.py` handles user registration and lookup. `cardfolder_router.py` handles folder CRUD. `cardset_router.py` handles card set CRUD with ownership checks, visibility filtering, and the copy feature. `card_router.py` handles card CRUD with ownership verification and update audit trails.

The `utils/` folder contains helper functions. `audio_text.py` will contain our regex-based function for generating audio text from display text.

The `__init__.py` files make each directory a Python package, which lets us import from them. These files can be empty — they just need to exist.

### 4.3 — The Two Foundational Files

Let us write the two files that every other file depends on: `database.py` and `main.py`.

**File: `database.py`**

```python
import os
from dotenv import load_dotenv
from supabase import create_client, Client

load_dotenv()

url: str = os.environ["SUPABASE_URL"]
key: str = os.environ["SUPABASE_KEY"]

supabase: Client = create_client(url, key)
```

We import `os` to access environment variables. We import `load_dotenv` to read our `.env` file. We import `create_client` and `Client` from the `supabase` package. We call `load_dotenv()`, read the two environment variables, and create a Supabase client stored in a variable called `supabase`. This `supabase` object is what every router will import to talk to the database.

**File: `main.py`**

```python
from fastapi import FastAPI
from routers import user_router, cardfolder_router, cardset_router, card_router

app = FastAPI(
    title="Flashcard API",
    description="Multi-user API for managing flashcard folders, sets, and cards with ownership, public sharing, and copy features",
    version="2.0.0"
)

app.include_router(user_router.router)
app.include_router(cardfolder_router.router)
app.include_router(cardset_router.router)
app.include_router(card_router.router)

@app.get("/")
def root():
    return {"message": "Flashcard API is running"}
```

Notice we now import and include four routers instead of three — the new `user_router` handles user registration and lookup. The version is `2.0.0` reflecting the multi-user feature set. When we run `uvicorn main:app --reload`, Uvicorn finds the `app` object in `main.py`, which now includes all endpoints from all four routers.

### Section 4 — Review

Let us review Section 4. We split our code into multiple files using FastAPI's `APIRouter` system — one router per entity (users, folders, cardsets, cards). We have a `models/` folder for Pydantic data shapes, a `routers/` folder for endpoint logic, and a `utils/` folder for helper functions. The `database.py` file creates a Supabase client. The `main.py` file creates the FastAPI app and includes all four routers. The key addition compared to a single-user system is the `user_router.py` and `user_models.py` files.

Four sections down, four to go. Next is Section 5 — Pydantic models with all the new multi-user fields.

### Section 4 — Q&A Table

| # | Question | Answer |
|---|----------|--------|
| 1 | What is an APIRouter? | A mini-application from FastAPI that handles a subset of endpoints. It uses the same decorators as the main app but must be included via `app.include_router()`. |
| 2 | Why do we split code into routers? | To keep files manageable. One file per entity (users, folders, cardsets, cards) is cleaner than one enormous file. |
| 3 | What does `database.py` export? | A `supabase` variable — a `Client` object connected to your Supabase project, ready to perform database operations. |
| 4 | What do `__init__.py` files do? | They make a directory a Python package, allowing `from routers import cardfolder_router` style imports. They can be empty. |
| 5 | How many routers do we now include? | Four: `user_router`, `cardfolder_router`, `cardset_router`, `card_router`. |
| 6 | Why was `user_router` added? | To handle user registration and lookup — multi-user features require knowing who is making each request. |
| 7 | How do you run the application? | `uvicorn main:app --reload` — this starts Uvicorn, pointing it at the `app` object in `main.py`, with auto-reload on file changes. |

---

---

## SECTION 5 — PYDANTIC MODELS

---

We are in Section 5. Let us recall where we are. Sections 1 through 3 gave us the conceptual foundation and the database (four tables with multi-user columns). Section 4 gave us the file structure with `database.py` and `main.py` ready. Now Section 5 builds the Pydantic models — the data validation layer that sits between the outside world and our database.

This section has **three parts**:
1. Why we need Pydantic models and what they do
2. The distinction between "Create", "Update", and "Response" models
3. The actual model code for all four entities

### 5.1 — Why Pydantic Models?

When someone sends a POST request to create a new flashcard, they send a JSON body. That JSON might look like `{"front_text_1": "El gato", "back_text_1": "The cat"}`. But what if someone sends `{"front_text_1": 12345}` — a number instead of a string? Or what if they send `{"nonexistent_field": "hello"}` — a field that does not exist in our schema?

Without validation, these bad requests would hit your database and either cause errors or silently corrupt your data. Pydantic prevents this. You define a class that describes the exact shape of acceptable data, and FastAPI uses that class to validate every incoming request before your endpoint function even runs. If the data is invalid, FastAPI automatically sends back a 422 Unprocessable Entity response with a detailed error message.

We need multiple kinds of models for each entity:

**Create models** define what data the client sends when creating a record. They do NOT include auto-generated fields like `id`, `created_at`, `updated_at`, or `updated_by`.

**Update models** define what can be changed after creation. They may exclude certain fields — for example, you should not change a card set's owner via an update endpoint.

**Response models** define what data the API sends back to the client. They DO include `id`, timestamps, and audit fields because the client needs to see those.

### 5.2 — The Model Code

**File: `models/user_models.py`**

```python
from pydantic import BaseModel
from datetime import datetime

class UserCreate(BaseModel):
    username: str
    email: str

class UserResponse(BaseModel):
    id: str
    username: str
    email: str
    created_at: datetime
```

This is the simplest model pair. `UserCreate` requires `username` and `email` — both mandatory strings, no optionals. `UserResponse` adds `id` and `created_at`. Notice there is no `UserUpdate` model — for simplicity, we will not support changing usernames or emails in this tutorial. You could add that later.

**File: `models/cardfolder_models.py`**

```python
from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class CardfolderCreate(BaseModel):
    name: str
    description: Optional[str] = None

class CardfolderResponse(BaseModel):
    id: str
    user_id: str
    name: str
    description: Optional[str] = None
    created_at: datetime
```

Folders now belong to a user. `CardfolderCreate` has `name` (required) and `description` (optional). Notice that, just like with card sets, `user_id` is NOT in the Create model — it will be set from the `x-user-id` header in the router, preventing clients from claiming to create folders on behalf of other users. `CardfolderResponse` includes `user_id` so the client can see who owns the folder, along with `id` and `created_at`.

**File: `models/cardset_models.py`**

```python
from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class CardsetCreate(BaseModel):
    cardfolder_id: str
    name: str
    description: Optional[str] = None
    is_public: bool = False

class CardsetUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    is_public: Optional[bool] = None

class CardsetResponse(BaseModel):
    id: str
    cardfolder_id: str
    user_id: str
    name: str
    description: Optional[str] = None
    is_public: bool
    created_at: datetime
```

Let us examine what changed compared to a single-user system. Three important observations:

First, `CardsetCreate` now includes `is_public` with a default of `False`. When creating a card set, the client can optionally set it to `True` to make it public immediately, but if they do not mention it, the card set defaults to private. Notice that `CardsetCreate` does NOT include `user_id`. Why? Because the user ID should come from the authenticated user making the request — it should never be something the client sets freely in the body. If you let the client specify `user_id` in the body, any user could claim to create a card set on behalf of another user. Instead, our endpoint will receive the `user_id` as a separate parameter (we will use a header for this in our simplified auth).

Second, we now have a `CardsetUpdate` model. It allows changing `name`, `description`, and `is_public` — all optional, because you might want to change only one of them. It does NOT include `cardfolder_id` or `user_id` — you cannot move a card set to a different folder or transfer ownership via a simple update.

Third, `CardsetResponse` includes `user_id` and `is_public` so the client can see who owns the set and whether it is public.

**File: `models/card_models.py`**

```python
from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class CardCreate(BaseModel):
    cardset_id: str
    front_text_1: Optional[str] = None
    front_audio_text_1: Optional[str] = None
    front_audio_1: Optional[str] = None
    front_image: Optional[str] = None
    back_text_1: Optional[str] = None
    back_audio_text_1: Optional[str] = None
    back_audio_1: Optional[str] = None
    back_image: Optional[str] = None

class CardUpdate(BaseModel):
    front_text_1: Optional[str] = None
    front_audio_text_1: Optional[str] = None
    front_audio_1: Optional[str] = None
    front_image: Optional[str] = None
    back_text_1: Optional[str] = None
    back_audio_text_1: Optional[str] = None
    back_audio_1: Optional[str] = None
    back_image: Optional[str] = None

class CardResponse(BaseModel):
    id: str
    cardset_id: str
    front_text_1: Optional[str] = None
    front_audio_text_1: Optional[str] = None
    front_audio_1: Optional[str] = None
    front_image: Optional[str] = None
    back_text_1: Optional[str] = None
    back_audio_text_1: Optional[str] = None
    back_audio_1: Optional[str] = None
    back_image: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    updated_by: Optional[str] = None
```

The card models now have two critical additions in `CardResponse`: `updated_at` (optional datetime, null if never updated) and `updated_by` (optional string, null if never updated or if the editing user was later deleted). These two fields expose the audit trail to the client. The client can see exactly when a card was last changed and who changed it.

Notice that `CardCreate` and `CardUpdate` do NOT include `updated_at` or `updated_by`. These are set automatically by our API code in the router — the client never provides them directly. The API sets `updated_at` to the current timestamp and `updated_by` to the requesting user's ID every time an update happens.

### 5.3 — A Note on Authentication: The `user_id` Header

In a production system, you would use proper authentication — JWT tokens, OAuth, Supabase Auth, etc. For this tutorial, we use a simplified approach: the client sends their `user_id` as an HTTP header called `x-user-id` with every request. Our endpoints read this header to know which user is making the request.

This is NOT secure for production — anyone could fake the header. But it lets us focus on the ownership and visibility logic without getting bogged down in authentication infrastructure. The concepts are identical regardless of how you identify the user; only the mechanism for extracting the user ID changes.

In FastAPI, you read a header using the `Header` dependency:

```python
from fastapi import Header

def my_endpoint(x_user_id: str = Header(...)):
    # x_user_id now contains the value of the x-user-id header
```

The `Header(...)` tells FastAPI to look for this value in the request headers. The `...` (Ellipsis) means it is required — the request fails with 422 if the header is missing. Note that FastAPI automatically converts the Python variable name `x_user_id` (with underscores) to look for the header `x-user-id` (with hyphens), because HTTP headers conventionally use hyphens.

### Section 5 — Review

Section 5 is complete. We built Pydantic models for all four entities. Users have Create and Response models. Folders have Create and Response models (unchanged from single-user). Card sets now include `is_public` in Create, have a new Update model, and include `user_id` and `is_public` in Response. Cards now include `updated_at` and `updated_by` in Response — these are set automatically by the API, never by the client. We also introduced our simplified authentication approach: the `x-user-id` header, read via FastAPI's `Header` dependency.

Five sections down. Section 6 is the big one — all the endpoints with ownership checks, visibility filters, and audit tracking.

### Section 5 — Q&A Table

| # | Question | Answer |
|---|----------|--------|
| 1 | Why does `CardsetCreate` NOT include `user_id`? | To prevent clients from claiming to create sets on behalf of another user. The user ID comes from the authenticated header instead. |
| 2 | Why does `CardsetCreate` include `is_public` with a default of `False`? | So card sets are private by default. The client can opt-in to public visibility but is not forced to specify it every time. |
| 3 | What are the two audit fields on `CardResponse`? | `updated_at` (when the card was last modified) and `updated_by` (which user made the last modification). |
| 4 | Why are `updated_at` and `updated_by` NOT in `CardCreate` or `CardUpdate`? | Because the API sets them automatically — the client should never control audit trail data directly. |
| 5 | What does `Header(...)` mean in FastAPI? | It tells FastAPI to read the value from an HTTP header. The `...` (Ellipsis) means the header is required. |
| 6 | How does FastAPI map `x_user_id` to the header `x-user-id`? | It automatically converts underscores to hyphens for header names — a FastAPI convention matching HTTP conventions. |
| 7 | Is the `x-user-id` header approach secure? | No — it is a learning simplification. Production systems use JWT tokens, OAuth, or Supabase Auth. But the ownership logic is identical. |

---

---

## SECTION 6 — BUILDING EVERY ENDPOINT

---

We have arrived at Section 6, the longest and most substantial section. Let us orient ourselves. We have: the conceptual understanding from Section 1, the environment from Section 2, the database tables (with multi-user columns) from Section 3, the project file structure from Section 4, and the Pydantic models (with ownership and audit fields) from Section 5. Section 6 now fills in the routers — the actual endpoint functions.

This section has **four major parts**, one per entity:
1. Part A: User endpoints (3 endpoints)
2. Part B: Card folder endpoints (4 endpoints)
3. Part C: Card set endpoints (7 endpoints, including ownership checks and visibility filters)
4. Part D: Card endpoints (6 endpoints, including ownership verification and audit tracking)

---

### Part A: User Endpoints

**File: `routers/user_router.py`**

We build three endpoints for users:
1. `POST /users` — register a new user
2. `GET /users` — list all users
3. `GET /users/{user_id}` — get one specific user

Here is the complete file:

```python
from fastapi import APIRouter, HTTPException
from models.user_models import UserCreate, UserResponse
from database import supabase
from typing import List

router = APIRouter(
    prefix="/users",
    tags=["Users"]
)


# ──────────────────────────────────────
# ENDPOINT 1: Register a new user
# ──────────────────────────────────────
@router.post("/", response_model=UserResponse)
def create_user(user: UserCreate):
    # Check if username already exists
    existing = supabase.table("users").select("id").eq("username", user.username).execute()
    if existing.data:
        raise HTTPException(status_code=409, detail="Username already taken")

    # Check if email already exists
    existing_email = supabase.table("users").select("id").eq("email", user.email).execute()
    if existing_email.data:
        raise HTTPException(status_code=409, detail="Email already registered")

    data = user.model_dump()
    result = supabase.table("users").insert(data).execute()

    if not result.data:
        raise HTTPException(status_code=400, detail="Failed to create user")

    return result.data[0]


# ──────────────────────────────────────
# ENDPOINT 2: Get all users
# ──────────────────────────────────────
@router.get("/", response_model=List[UserResponse])
def get_all_users():
    result = supabase.table("users").select("*").execute()
    return result.data


# ──────────────────────────────────────
# ENDPOINT 3: Get one user by ID
# ──────────────────────────────────────
@router.get("/{user_id}", response_model=UserResponse)
def get_user(user_id: str):
    result = supabase.table("users").select("*").eq("id", user_id).execute()

    if not result.data:
        raise HTTPException(status_code=404, detail="User not found")

    return result.data[0]
```

Let us walk through the key new concept here: **HTTP status code 409 (Conflict).**

In Endpoint 1, before inserting a new user, we check whether the username or email already exists. If either does, we raise an `HTTPException` with status code `409`. Status 409 means "Conflict" — the request is valid in its format, but it conflicts with the current state of the server (a user with that username already exists). This is more specific and informative than returning a generic 400 (Bad Request). The database's UNIQUE constraints would also catch this, but checking explicitly lets us return a clear message like "Username already taken" instead of a raw database error.

---

### Part B: Card Folder Endpoints

**File: `routers/cardfolder_router.py`**

Folders now belong to a user. Every folder has a `user_id`, and only the owner can modify or delete their folders. We build five endpoints:
1. `POST /cardfolders` — create a new folder (owner is the requesting user)
2. `GET /cardfolders/my` — get all folders owned by the requesting user
3. `GET /cardfolders/{folder_id}` — get one specific folder
4. `PUT /cardfolders/{folder_id}` — update a folder (owner only)
5. `DELETE /cardfolders/{folder_id}` — delete a folder (owner only, cascades to card sets and cards)

```python
from fastapi import APIRouter, HTTPException, Header
from models.cardfolder_models import CardfolderCreate, CardfolderResponse
from database import supabase
from typing import List

router = APIRouter(
    prefix="/cardfolders",
    tags=["Card Folders"]
)


# ──────────────────────────────────────────────────────────────
# HELPER: Verify the requesting user exists in the database
# ──────────────────────────────────────────────────────────────
def verify_user(user_id: str):
    result = supabase.table("users").select("id").eq("id", user_id).execute()
    if not result.data:
        raise HTTPException(status_code=401, detail="User not found — invalid x-user-id header")


# ──────────────────────────────────────────────────────────────
# HELPER: Verify the requesting user owns the given folder
# ──────────────────────────────────────────────────────────────
def verify_folder_ownership(folder_id: str, user_id: str):
    result = supabase.table("cardfolders").select("*").eq("id", folder_id).execute()
    if not result.data:
        raise HTTPException(status_code=404, detail="Folder not found")
    folder = result.data[0]
    if folder["user_id"] != user_id:
        raise HTTPException(status_code=403, detail="You do not own this folder")
    return folder


# ──────────────────────────────────────
# ENDPOINT 1: Create a new folder
# ──────────────────────────────────────
@router.post("/", response_model=CardfolderResponse)
def create_cardfolder(folder: CardfolderCreate, x_user_id: str = Header(...)):
    verify_user(x_user_id)

    data = folder.model_dump()
    data["user_id"] = x_user_id  # Set the owner to the requesting user

    result = supabase.table("cardfolders").insert(data).execute()

    if not result.data:
        raise HTTPException(status_code=400, detail="Failed to create folder")

    return result.data[0]


# ──────────────────────────────────────────
# ENDPOINT 2: Get all folders owned by me
# ──────────────────────────────────────────
@router.get("/my", response_model=List[CardfolderResponse])
def get_my_cardfolders(x_user_id: str = Header(...)):
    verify_user(x_user_id)
    result = supabase.table("cardfolders").select("*").eq("user_id", x_user_id).execute()
    return result.data


# ──────────────────────────────────────
# ENDPOINT 3: Get one folder by ID
# ──────────────────────────────────────
@router.get("/{folder_id}", response_model=CardfolderResponse)
def get_cardfolder(folder_id: str):
    result = supabase.table("cardfolders").select("*").eq("id", folder_id).execute()

    if not result.data:
        raise HTTPException(status_code=404, detail="Folder not found")

    return result.data[0]


# ──────────────────────────────────────────
# ENDPOINT 4: Update a folder (owner only)
# ──────────────────────────────────────────
@router.put("/{folder_id}", response_model=CardfolderResponse)
def update_cardfolder(folder_id: str, folder: CardfolderCreate, x_user_id: str = Header(...)):
    verify_user(x_user_id)
    verify_folder_ownership(folder_id, x_user_id)

    data = folder.model_dump()
    result = supabase.table("cardfolders").update(data).eq("id", folder_id).execute()

    if not result.data:
        raise HTTPException(status_code=400, detail="Failed to update folder")

    return result.data[0]


# ──────────────────────────────────────────
# ENDPOINT 5: Delete a folder (owner only)
# ──────────────────────────────────────────
@router.delete("/{folder_id}")
def delete_cardfolder(folder_id: str, x_user_id: str = Header(...)):
    verify_user(x_user_id)
    verify_folder_ownership(folder_id, x_user_id)

    result = supabase.table("cardfolders").delete().eq("id", folder_id).execute()

    if not result.data:
        raise HTTPException(status_code=404, detail="Folder not found")

    return {"message": "Folder deleted successfully", "deleted": result.data[0]}
```

Let us note what changed compared to the old shared-folder approach. This router now follows the exact same ownership patterns as the card set router — which is a good sign, it means the design is consistent.

**The `verify_folder_ownership` helper** works identically to `verify_ownership` in the cardset router: fetch the folder, check it exists (404 if not), check the user owns it (403 if not). This pattern repeats across every entity that has an owner.

**Endpoint 1 (Create) — setting `user_id` from the header.** Just like creating a card set, the owner is determined by the `x-user-id` header, not by the request body. The line `data["user_id"] = x_user_id` establishes ownership.

**Endpoint 2 (Get my folders) — filtered by owner.** The query `.eq("user_id", x_user_id)` returns only folders belonging to the requesting user. Each user sees only their own organizational structure.

**Endpoints 4 and 5 (Update and Delete) — owner only.** Both call `verify_user` then `verify_folder_ownership`. If either check fails, the endpoint aborts. Only the owner can rename, edit, or delete their folders.

---

### Part C: Card Set Endpoints — Ownership, Visibility, and Copying

**File: `routers/cardset_router.py`**

This is where the multi-user features hit hardest. Card sets are owned by users, can be public or private, and can be copied. We build seven endpoints:
1. `POST /cardsets` — create a new card set (owner is the requesting user)
2. `GET /cardsets/my` — get all card sets owned by the requesting user
3. `GET /cardsets/public` — get all public card sets (from any user)
4. `GET /cardsets/{cardset_id}` — get one specific card set (visibility enforced)
5. `GET /cardsets/folder/{folder_id}` — get card sets in a folder (visibility enforced)
6. `PUT /cardsets/{cardset_id}` — update a card set (owner only)
7. `DELETE /cardsets/{cardset_id}` — delete a card set (owner only)

The copy feature will be built in Section 8 — it has its own endpoint that we will add to this router.

Here is the complete file. It is significantly longer than the single-user version because of ownership checks and visibility filtering:

```python
from fastapi import APIRouter, HTTPException, Header
from models.cardset_models import CardsetCreate, CardsetUpdate, CardsetResponse
from database import supabase
from typing import List

router = APIRouter(
    prefix="/cardsets",
    tags=["Card Sets"]
)


# ──────────────────────────────────────────────────────────────
# HELPER: Verify the requesting user exists in the database
# ──────────────────────────────────────────────────────────────
def verify_user(user_id: str):
    result = supabase.table("users").select("id").eq("id", user_id).execute()
    if not result.data:
        raise HTTPException(status_code=401, detail="User not found — invalid x-user-id header")


# ──────────────────────────────────────────────────────────────
# HELPER: Verify the requesting user owns the given card set
# Returns the card set data if ownership is confirmed
# ──────────────────────────────────────────────────────────────
def verify_ownership(cardset_id: str, user_id: str):
    result = supabase.table("cardsets").select("*").eq("id", cardset_id).execute()
    if not result.data:
        raise HTTPException(status_code=404, detail="Card set not found")
    cardset = result.data[0]
    if cardset["user_id"] != user_id:
        raise HTTPException(status_code=403, detail="You do not own this card set")
    return cardset


# ──────────────────────────────────────
# ENDPOINT 1: Create a new card set
# ──────────────────────────────────────
@router.post("/", response_model=CardsetResponse)
def create_cardset(cardset: CardsetCreate, x_user_id: str = Header(...)):
    verify_user(x_user_id)

    # Verify the parent folder exists and belongs to this user
    folder_check = supabase.table("cardfolders").select("*").eq("id", cardset.cardfolder_id).execute()
    if not folder_check.data:
        raise HTTPException(status_code=404, detail="Parent folder not found")
    if folder_check.data[0]["user_id"] != x_user_id:
        raise HTTPException(status_code=403, detail="You do not own the parent folder")

    data = cardset.model_dump()
    data["user_id"] = x_user_id  # Set the owner to the requesting user

    result = supabase.table("cardsets").insert(data).execute()

    if not result.data:
        raise HTTPException(status_code=400, detail="Failed to create card set")

    return result.data[0]


# ──────────────────────────────────────────
# ENDPOINT 2: Get all card sets owned by me
# ──────────────────────────────────────────
@router.get("/my", response_model=List[CardsetResponse])
def get_my_cardsets(x_user_id: str = Header(...)):
    verify_user(x_user_id)
    result = supabase.table("cardsets").select("*").eq("user_id", x_user_id).execute()
    return result.data


# ──────────────────────────────────────────
# ENDPOINT 3: Get all public card sets
# ──────────────────────────────────────────
@router.get("/public", response_model=List[CardsetResponse])
def get_public_cardsets():
    result = supabase.table("cardsets").select("*").eq("is_public", True).execute()
    return result.data


# ──────────────────────────────────────────────────────────
# ENDPOINT 4: Get one card set by ID (visibility enforced)
# ──────────────────────────────────────────────────────────
@router.get("/{cardset_id}", response_model=CardsetResponse)
def get_cardset(cardset_id: str, x_user_id: str = Header(default=None)):
    result = supabase.table("cardsets").select("*").eq("id", cardset_id).execute()

    if not result.data:
        raise HTTPException(status_code=404, detail="Card set not found")

    cardset = result.data[0]

    # If the set is private, only the owner can see it
    if not cardset["is_public"] and cardset["user_id"] != x_user_id:
        raise HTTPException(status_code=403, detail="This card set is private")

    return cardset


# ──────────────────────────────────────────────────────────────────
# ENDPOINT 5: Get card sets in a folder (visibility enforced)
# ──────────────────────────────────────────────────────────────────
@router.get("/folder/{folder_id}", response_model=List[CardsetResponse])
def get_cardsets_by_folder(folder_id: str, x_user_id: str = Header(default=None)):
    result = supabase.table("cardsets").select("*").eq("cardfolder_id", folder_id).execute()

    # Filter: show public sets + sets owned by the requesting user
    visible = []
    for cs in result.data:
        if cs["is_public"] or cs["user_id"] == x_user_id:
            visible.append(cs)

    return visible


# ──────────────────────────────────────────────
# ENDPOINT 6: Update a card set (owner only)
# ──────────────────────────────────────────────
@router.put("/{cardset_id}", response_model=CardsetResponse)
def update_cardset(cardset_id: str, cardset: CardsetUpdate, x_user_id: str = Header(...)):
    verify_user(x_user_id)
    verify_ownership(cardset_id, x_user_id)

    data = cardset.model_dump(exclude_unset=True)

    if not data:
        raise HTTPException(status_code=400, detail="No fields to update")

    result = supabase.table("cardsets").update(data).eq("id", cardset_id).execute()

    if not result.data:
        raise HTTPException(status_code=400, detail="Failed to update card set")

    return result.data[0]


# ──────────────────────────────────────────────
# ENDPOINT 7: Delete a card set (owner only)
# ──────────────────────────────────────────────
@router.delete("/{cardset_id}")
def delete_cardset(cardset_id: str, x_user_id: str = Header(...)):
    verify_user(x_user_id)
    verify_ownership(cardset_id, x_user_id)

    result = supabase.table("cardsets").delete().eq("id", cardset_id).execute()

    if not result.data:
        raise HTTPException(status_code=404, detail="Card set not found")

    return {"message": "Card set deleted successfully", "deleted": result.data[0]}
```

This is the most complex router so far. Let us examine every new concept in detail.

**The `verify_user` helper function.** This function takes a user ID, queries the `users` table, and raises a 401 (Unauthorized) if the user does not exist. We call it at the start of any endpoint that requires a known user. This prevents requests with fake or nonexistent user IDs from proceeding.

**The `verify_ownership` helper function.** This function takes a card set ID and a user ID. It first fetches the card set from the database. If the card set does not exist, it raises 404 (Not Found). If the card set exists but its `user_id` does not match the requesting user, it raises 403 (Forbidden). The difference between 401 and 403 is important: 401 means "we do not know who you are" (authentication failure), while 403 means "we know who you are, but you are not allowed to do this" (authorization failure).

**Endpoint 1 (Create) — setting `user_id` from the header.** Look at the line `data["user_id"] = x_user_id`. This is where ownership is established. The client's body contains the card set name, description, folder, and visibility — but the owner is determined by the header, not the body. The client cannot claim ownership on behalf of another user. This is the direct consequence of our design decision in Section 5 to exclude `user_id` from `CardsetCreate`.

**Endpoint 2 (Get my card sets) — filtered by owner.** The query `.eq("user_id", x_user_id)` retrieves only card sets where the owner matches the requesting user. This endpoint always returns everything the user owns, regardless of public/private status.

**Endpoint 3 (Get public card sets) — no authentication needed.** Notice this endpoint does NOT require `x_user_id`. Anyone can browse public card sets without identifying themselves. The query `.eq("is_public", True)` retrieves only public sets.

**Endpoint 4 (Get one card set) — visibility enforcement.** Here we use `Header(default=None)` instead of `Header(...)`. The difference: `Header(...)` means the header is required and the request fails without it. `Header(default=None)` means the header is optional — it defaults to `None` if not provided. Why optional here? Because a public card set should be viewable by anyone, even anonymous users. But if the set is private, we need to check if the requester is the owner. The logic is: if the set is public, return it regardless. If private, check if `user_id` matches the owner — and if not (or if no header was provided), return 403.

**Endpoint 5 (Get sets in a folder) — Python-side filtering.** Supabase does not easily support an OR condition like `WHERE is_public = true OR user_id = 'xyz'` in a single chained query. So we fetch all card sets in the folder and filter in Python: keep those that are either public or owned by the requesting user. For small to medium datasets this is perfectly fine. For very large datasets, you would use a Supabase stored procedure or an `.or_()` filter.

**Endpoints 6 and 7 (Update and Delete) — owner only.** Both call `verify_user` then `verify_ownership`. If either check fails, the endpoint aborts with the appropriate error. Only the owner can modify or delete a card set.

---

### Part D: Card Endpoints — Ownership Verification and Audit Tracking

**File: `routers/card_router.py`**

Cards live inside card sets. To determine if a user can create, update, or delete a card, we check whether they own the **parent card set**. Additionally, every update now writes `updated_at` and `updated_by` to the card record. We build six endpoints:
1. `POST /cards` — create a new card (must own the parent card set)
2. `GET /cards/{card_id}` — get one specific card
3. `GET /cards/cardset/{cardset_id}` — get all cards in a card set (visibility enforced)
4. `PUT /cards/{card_id}` — update a card (must own parent card set, writes audit fields)
5. `DELETE /cards/{card_id}` — delete a card (must own parent card set)
6. `GET /cards/cardset/{cardset_id}/updates` — get update history for all cards in a set

```python
from fastapi import APIRouter, HTTPException, Header
from models.card_models import CardCreate, CardUpdate, CardResponse
from database import supabase
from utils.audio_text import generate_audio_text
from typing import List
from datetime import datetime, timezone

router = APIRouter(
    prefix="/cards",
    tags=["Cards"]
)


# ──────────────────────────────────────────────────────────────
# HELPER: Verify user exists
# ──────────────────────────────────────────────────────────────
def verify_user(user_id: str):
    result = supabase.table("users").select("id").eq("id", user_id).execute()
    if not result.data:
        raise HTTPException(status_code=401, detail="User not found — invalid x-user-id header")


# ──────────────────────────────────────────────────────────────
# HELPER: Verify the requesting user owns the card set
# that a card belongs to (or will belong to)
# ──────────────────────────────────────────────────────────────
def verify_cardset_ownership(cardset_id: str, user_id: str):
    result = supabase.table("cardsets").select("*").eq("id", cardset_id).execute()
    if not result.data:
        raise HTTPException(status_code=404, detail="Parent card set not found")
    if result.data[0]["user_id"] != user_id:
        raise HTTPException(status_code=403, detail="You do not own the parent card set")
    return result.data[0]


# ──────────────────────────────────────────────────────────────
# HELPER: Given a card ID, look up which cardset it belongs to
# and verify ownership. Returns the card data.
# ──────────────────────────────────────────────────────────────
def get_card_and_verify_ownership(card_id: str, user_id: str):
    card_result = supabase.table("cards").select("*").eq("id", card_id).execute()
    if not card_result.data:
        raise HTTPException(status_code=404, detail="Card not found")
    card = card_result.data[0]
    verify_cardset_ownership(card["cardset_id"], user_id)
    return card


# ──────────────────────────────────────
# ENDPOINT 1: Create a new card
# ──────────────────────────────────────
@router.post("/", response_model=CardResponse)
def create_card(card: CardCreate, x_user_id: str = Header(...)):
    verify_user(x_user_id)
    verify_cardset_ownership(card.cardset_id, x_user_id)

    data = card.model_dump()

    # Auto-generate audio text if not provided
    if data.get("front_text_1") and not data.get("front_audio_text_1"):
        data["front_audio_text_1"] = generate_audio_text(data["front_text_1"])

    if data.get("back_text_1") and not data.get("back_audio_text_1"):
        data["back_audio_text_1"] = generate_audio_text(data["back_text_1"])

    result = supabase.table("cards").insert(data).execute()

    if not result.data:
        raise HTTPException(status_code=400, detail="Failed to create card")

    return result.data[0]


# ──────────────────────────────────────
# ENDPOINT 2: Get one card by ID
# ──────────────────────────────────────
@router.get("/{card_id}", response_model=CardResponse)
def get_card(card_id: str, x_user_id: str = Header(default=None)):
    card_result = supabase.table("cards").select("*").eq("id", card_id).execute()
    if not card_result.data:
        raise HTTPException(status_code=404, detail="Card not found")

    card = card_result.data[0]

    # Check visibility of the parent card set
    cardset = supabase.table("cardsets").select("*").eq("id", card["cardset_id"]).execute()
    if cardset.data:
        cs = cardset.data[0]
        if not cs["is_public"] and cs["user_id"] != x_user_id:
            raise HTTPException(status_code=403, detail="This card belongs to a private card set")

    return card


# ────────────────────────────────────────────────────────────────
# ENDPOINT 3: Get all cards in a card set (visibility enforced)
# ────────────────────────────────────────────────────────────────
@router.get("/cardset/{cardset_id}", response_model=List[CardResponse])
def get_cards_by_cardset(cardset_id: str, x_user_id: str = Header(default=None)):
    # Check that the card set exists and is visible
    cs_result = supabase.table("cardsets").select("*").eq("id", cardset_id).execute()
    if not cs_result.data:
        raise HTTPException(status_code=404, detail="Card set not found")

    cs = cs_result.data[0]
    if not cs["is_public"] and cs["user_id"] != x_user_id:
        raise HTTPException(status_code=403, detail="This card set is private")

    result = supabase.table("cards").select("*").eq("cardset_id", cardset_id).execute()
    return result.data


# ──────────────────────────────────────────────────────────────────
# ENDPOINT 4: Update a card (owner only, writes audit fields)
# ──────────────────────────────────────────────────────────────────
@router.put("/{card_id}", response_model=CardResponse)
def update_card(card_id: str, card: CardUpdate, x_user_id: str = Header(...)):
    verify_user(x_user_id)
    get_card_and_verify_ownership(card_id, x_user_id)

    data = card.model_dump(exclude_unset=True)

    # Regenerate audio text if display text changed but audio text not explicitly set
    if "front_text_1" in data and "front_audio_text_1" not in data:
        if data["front_text_1"] is not None:
            data["front_audio_text_1"] = generate_audio_text(data["front_text_1"])
        else:
            data["front_audio_text_1"] = None

    if "back_text_1" in data and "back_audio_text_1" not in data:
        if data["back_text_1"] is not None:
            data["back_audio_text_1"] = generate_audio_text(data["back_text_1"])
        else:
            data["back_audio_text_1"] = None

    if not data:
        raise HTTPException(status_code=400, detail="No fields to update")

    # ── AUDIT TRAIL: Write update timestamp and user ──
    data["updated_at"] = datetime.now(timezone.utc).isoformat()
    data["updated_by"] = x_user_id

    result = supabase.table("cards").update(data).eq("id", card_id).execute()

    if not result.data:
        raise HTTPException(status_code=400, detail="Failed to update card")

    return result.data[0]


# ──────────────────────────────────────────────
# ENDPOINT 5: Delete a card (owner only)
# ──────────────────────────────────────────────
@router.delete("/{card_id}")
def delete_card(card_id: str, x_user_id: str = Header(...)):
    verify_user(x_user_id)
    get_card_and_verify_ownership(card_id, x_user_id)

    result = supabase.table("cards").delete().eq("id", card_id).execute()

    if not result.data:
        raise HTTPException(status_code=404, detail="Card not found")

    return {"message": "Card deleted successfully", "deleted": result.data[0]}


# ──────────────────────────────────────────────────────────────────────
# ENDPOINT 6: Get update history for all cards in a card set
# Shows each card's last update timestamp and who updated it
# ──────────────────────────────────────────────────────────────────────
@router.get("/cardset/{cardset_id}/updates")
def get_card_updates(cardset_id: str, x_user_id: str = Header(default=None)):
    # Visibility check
    cs_result = supabase.table("cardsets").select("*").eq("id", cardset_id).execute()
    if not cs_result.data:
        raise HTTPException(status_code=404, detail="Card set not found")

    cs = cs_result.data[0]
    if not cs["is_public"] and cs["user_id"] != x_user_id:
        raise HTTPException(status_code=403, detail="This card set is private")

    result = supabase.table("cards").select(
        "id, front_text_1, back_text_1, created_at, updated_at, updated_by"
    ).eq("cardset_id", cardset_id).execute()

    return result.data
```

Let us examine the new concepts in this router in detail. There are several important additions compared to the single-user version.

**The `verify_cardset_ownership` helper.** Cards do not have a direct `user_id` column — ownership is determined by the parent card set. To check if a user can modify a card, we look up which card set the card belongs to, then check if that card set's `user_id` matches the requesting user. This two-step lookup is encapsulated in the helpers `verify_cardset_ownership` (when we know the card set ID) and `get_card_and_verify_ownership` (when we have a card ID and need to find its card set first).

**Endpoint 1 (Create) — ownership gate at the card set level.** When creating a card, the client provides `cardset_id` in the body. Before inserting, we verify the requesting user owns that card set. This prevents User B from adding cards to User A's card set. The audio text auto-generation is the same as in the single-user version.

**Endpoints 2 and 3 (Read) — visibility inherited from card set.** When someone asks for a specific card or all cards in a card set, we check the parent card set's `is_public` flag. If the set is private and the requester is not the owner, we return 403. This means visibility cascades: making a card set private hides all its cards too. You do not need per-card visibility flags.

**Endpoint 4 (Update) — the audit trail.** This is where `updated_at` and `updated_by` come to life. After assembling the update data and handling audio text regeneration, we add two lines:

The line `data["updated_at"] = datetime.now(timezone.utc).isoformat()` sets the update timestamp to the current moment in UTC, formatted as an ISO 8601 string (like `"2025-03-15T14:30:00+00:00"`). We use `timezone.utc` to ensure consistency regardless of the server's local timezone.

The line `data["updated_by"] = x_user_id` records which user made this edit. Together, these two fields create a permanent record: "This card was last modified on March 15, 2025 at 2:30 PM UTC by user abc-123."

Note that we import `datetime` and `timezone` from the `datetime` module at the top of the file. This is a standard library import — no new packages needed.

**Endpoint 6 (Update history) — a read-only audit view.** This endpoint returns a lightweight view of all cards in a card set, showing only identification fields (`id`, `front_text_1`, `back_text_1`) and audit fields (`created_at`, `updated_at`, `updated_by`). The `select()` call specifies only the columns we want, rather than `"*"`. This is useful for dashboards or admin views where you want to see at a glance which cards have been recently modified and by whom.

---

### Section 6 — Full Endpoint Summary

Let us now list every endpoint across all four routers:

| # | Method | URL | Auth Required | Purpose |
|---|--------|-----|---------------|---------|
| 1 | POST | `/users/` | No | Register a new user |
| 2 | GET | `/users/` | No | List all users |
| 3 | GET | `/users/{user_id}` | No | Get one user |
| 4 | POST | `/cardfolders/` | Yes | Create a folder (you become owner) |
| 5 | GET | `/cardfolders/my` | Yes | Get all your folders |
| 6 | GET | `/cardfolders/{folder_id}` | No | Get one folder |
| 7 | PUT | `/cardfolders/{folder_id}` | Yes | Update a folder (owner only) |
| 8 | DELETE | `/cardfolders/{folder_id}` | Yes | Delete a folder (owner only) + cascade |
| 9 | POST | `/cardsets/` | Yes | Create a card set (you become owner) |
| 10 | GET | `/cardsets/my` | Yes | Get all your card sets |
| 11 | GET | `/cardsets/public` | No | Get all public card sets |
| 12 | GET | `/cardsets/{cardset_id}` | Optional | Get one card set (visibility enforced) |
| 13 | GET | `/cardsets/folder/{folder_id}` | Optional | Get card sets in a folder (filtered) |
| 14 | PUT | `/cardsets/{cardset_id}` | Yes | Update a card set (owner only) |
| 15 | DELETE | `/cardsets/{cardset_id}` | Yes | Delete a card set (owner only) |
| 16 | POST | `/cards/` | Yes | Create a card (must own card set) |
| 17 | GET | `/cards/{card_id}` | Optional | Get one card (visibility enforced) |
| 18 | GET | `/cards/cardset/{cardset_id}` | Optional | Get all cards in a set (visibility enforced) |
| 19 | PUT | `/cards/{card_id}` | Yes | Update a card (owner only, writes audit) |
| 20 | DELETE | `/cards/{card_id}` | Yes | Delete a card (owner only) |
| 21 | GET | `/cards/cardset/{cardset_id}/updates` | Optional | View update history for a set |

That is 21 endpoints across four routers. We will add one more endpoint in Section 8 — the copy endpoint — bringing the total to 22.

### Section 6 — Review

Section 6 is the heart of the application. Users can register and be looked up (3 endpoints). Folders are owned by users, with ownership checks on create, update, and delete (5 endpoints). Card sets enforce ownership via `verify_ownership` and visibility via `is_public` checks, and the create endpoint also verifies that the parent folder belongs to the same user (7 endpoints). Cards inherit visibility from their parent card set and verify ownership by looking up the parent card set's owner (6 endpoints). Every card update writes `updated_at` and `updated_by` for the audit trail.

The key patterns: `Header(...)` for mandatory authentication. `Header(default=None)` for optional authentication. Status 401 for unknown users. Status 403 for known users who lack permission. Status 409 for conflicts like duplicate usernames. Helper functions encapsulate repeated ownership checks.

Six sections done. Two to go — audio text generation (Section 7) and the copy feature (Section 8).

### Section 6 — Q&A Table

| # | Question | Answer |
|---|----------|--------|
| 1 | What does `verify_ownership` do? | Fetches the card set, checks if it exists (404 if not), then checks if the requesting user is the owner (403 if not). |
| 2 | Why does `Header(default=None)` differ from `Header(...)`? | `Header(...)` is required — missing it returns 422. `Header(default=None)` is optional — it defaults to None for anonymous access. |
| 3 | What HTTP status code means "you exist but lack permission"? | 403 Forbidden. Compare with 401 Unauthorized which means "we don't know who you are." |
| 4 | How is card ownership determined? | By checking the parent card set's `user_id`. Cards do not have their own `user_id` column. |
| 5 | What two lines create the audit trail on card updates? | `data["updated_at"] = datetime.now(timezone.utc).isoformat()` and `data["updated_by"] = x_user_id`. |
| 6 | Why use `timezone.utc` instead of just `datetime.now()`? | To ensure timestamps are in UTC regardless of the server's local timezone, preventing inconsistencies across deployments. |
| 7 | What does the `/updates` endpoint return? | A lightweight view with each card's ID, text snippets, creation date, last update date, and who updated it. |
| 8 | Why does endpoint 5 filter in Python instead of in Supabase? | Supabase's chained query API does not easily support OR conditions. Python filtering is simple and correct for moderate data sizes. |
| 9 | What prevents User B from adding cards to User A's card set? | The create card endpoint calls `verify_cardset_ownership`, which checks that the card set's `user_id` matches the requesting user. |
| 10 | What does `model_dump(exclude_unset=True)` prevent? | It prevents unmentioned fields from being sent as None, which would overwrite existing data in the database. |

---

---

## SECTION 7 — AUDIO TEXT GENERATION WITH REGULAR EXPRESSIONS

---

We are in Section 7. Sections 1 through 6 built the complete multi-user API: environment, database with four tables, project structure, models with ownership and audit fields, and all endpoints with ownership checks and visibility filters. The only piece missing is the `generate_audio_text` function that we import in the card router. This function takes a display text string and transforms it into a version optimized for text-to-speech audio.

This section has **three parts**:
1. Why audio text needs to differ from display text
2. Understanding regular expressions for this purpose
3. The complete implementation with multiple regex rules

### 7.1 — Why Audio Text Differs from Display Text

Consider a flashcard for learning Spanish. The front might display: `El gato (the cat) [m.]`. This is excellent for visual reading — the learner sees the Spanish word, an English translation in parentheses, and a grammatical annotation in square brackets indicating masculine gender.

But if you send this exact string to a text-to-speech engine, it would robotically read "El gato open parenthesis the cat close parenthesis open bracket m period close bracket." That is terrible. What you want the TTS engine to read is simply: "El gato." Or perhaps "El gato. The cat" — spoken as two clean phrases.

So we need a function that takes the display text and strips or transforms certain patterns: parenthetical hints, square bracket annotations, special notation symbols, and so on. Regular expressions are the perfect tool for this because they let us describe patterns rather than specific strings.

### 7.2 — Understanding the Regex Patterns

Let us establish a set of reasonable transformation rules. These are customizable — you can add, remove, or modify rules later. We will implement five rules:

**Rule 1: Remove content in square brackets.** The pattern `\[.*?\]` matches an opening square bracket, then any characters (as few as possible — that is what `.*?` means, the `?` makes it non-greedy), then a closing square bracket. Input: `"El gato [m.]"` becomes `"El gato"`.

**Rule 2: Remove content in parentheses.** The pattern `\(.*?\)` works identically but for parentheses. Input: `"El gato (the cat)"` becomes `"El gato"`.

**Rule 3: Remove slash-separated alternatives, keeping only the first.** Sometimes a flashcard shows `"rojo/a"` meaning the word can be "rojo" or "roja." For audio, we just want "rojo." The pattern `(\w+)/\w+` matches a word, a slash, and another word, and replaces the whole match with just the first word (captured in group 1).

**Rule 4: Remove leading numbers and dots.** If cards are numbered like `"1. El gato"`, we strip the numbering for audio. The pattern `^\d+\.\s*` matches one or more digits followed by a dot and optional whitespace at the start of the string.

**Rule 5: Clean up extra whitespace.** After all the removals, we might have double spaces or leading/trailing whitespace. We collapse multiple spaces into one and strip the edges.

### 7.3 — The Complete Implementation

**File: `utils/audio_text.py`**

```python
import re


def generate_audio_text(display_text: str) -> str:
    """
    Transform display text into audio-friendly text by removing
    annotations, hints, and formatting that would sound unnatural
    when read aloud by a text-to-speech engine.

    Rules applied in order:
    1. Remove content in square brackets: [m.] [noun] [informal]
    2. Remove content in parentheses: (the cat) (lit. house)
    3. Simplify slash alternatives to first word: rojo/a -> rojo
    4. Remove leading numbering: 1. 2. 3.
    5. Clean up whitespace
    """
    text = display_text

    # Rule 1: Remove square bracket content
    # \[   matches a literal opening bracket
    # .*?  matches any characters, non-greedy (as few as possible)
    # \]   matches a literal closing bracket
    text = re.sub(r'\[.*?\]', '', text)

    # Rule 2: Remove parenthetical content
    # \(   matches a literal opening parenthesis
    # .*?  matches any characters, non-greedy
    # \)   matches a literal closing parenthesis
    text = re.sub(r'\(.*?\)', '', text)

    # Rule 3: Simplify slash alternatives — keep only first word
    # (\w+)  captures one or more word characters (the part we keep)
    # /      matches a literal slash
    # \w+    matches one or more word characters (the part we discard)
    # \1     in the replacement refers to the first captured group
    text = re.sub(r'(\w+)/\w+', r'\1', text)

    # Rule 4: Remove leading numbering like "1. " or "23. "
    # ^      anchors to the start of the string
    # \d+    matches one or more digits
    # \.     matches a literal dot
    # \s*    matches zero or more whitespace characters
    text = re.sub(r'^\d+\.\s*', '', text)

    # Rule 5: Collapse multiple spaces into one
    # \s+    matches one or more whitespace characters
    text = re.sub(r'\s+', ' ', text)

    # Final strip to remove leading/trailing whitespace
    text = text.strip()

    return text
```

Let us walk through a complete example to see all five rules working in sequence.

Starting text: `"3. El gato rojo/a (the red cat) [m./f.]"`

After Rule 1 (remove square brackets): `"3. El gato rojo/a (the red cat) "`
After Rule 2 (remove parentheses): `"3. El gato rojo/a  "`
After Rule 3 (simplify slashes): `"3. El gato rojo  "`
After Rule 4 (remove numbering): `"El gato rojo  "`
After Rule 5 (collapse whitespace): `"El gato rojo"`
After final strip: `"El gato rojo"`

The result is clean, natural text that a TTS engine can read smoothly.

**Important detail about `re.sub`:** The function `re.sub` takes three arguments — `re.sub(pattern, replacement, string)`. It finds all occurrences of `pattern` in `string` and replaces each with `replacement`. In Rules 1, 2, and 4, the replacement is an empty string `''` — we are deleting the matched text. In Rule 3, the replacement is `r'\1'` which means "the content captured by the first set of parentheses in the pattern." The `r` prefix makes it a raw string so the backslash is not interpreted as an escape character.

**Why non-greedy (`.*?`) in Rules 1 and 2?** Consider the text `"(one) word (two)"`. A greedy pattern `\(.*\)` would match from the first `(` all the way to the last `)`, capturing `"(one) word (two)"` as a single match — removing the word between the parentheses too. The non-greedy `\(.*?\)` matches the shortest possible span, so it matches `"(one)"` and `"(two)"` separately, preserving the word between them.

### Section 7 — Review

Section 7 is done. We built a `generate_audio_text` function in `utils/audio_text.py` that applies five regex transformation rules: remove square bracket content, remove parenthetical content, simplify slash alternatives, remove leading numbering, and collapse whitespace. This function is called automatically in the card router's create and update endpoints when the client provides display text but not explicit audio text. The rules are easily customizable by adding or modifying `re.sub` calls.

Seven sections done. One to go — the copy feature.

### Section 7 — Q&A Table

| # | Question | Answer |
|---|----------|--------|
| 1 | What does `re.sub(pattern, replacement, string)` do? | Finds all matches of `pattern` in `string` and replaces each with `replacement`. Returns the modified string. |
| 2 | What does `.*?` mean versus `.*`? | `.*?` is non-greedy — matches as few characters as possible. `.*` is greedy — matches as many as possible. |
| 3 | Why is non-greedy important for bracket removal? | To match each bracket pair individually. Greedy would match from the first `[` to the last `]`, removing everything between multiple pairs. |
| 4 | What does `r'\1'` mean in a replacement string? | It refers to the first captured group (text inside the first set of parentheses in the pattern). |
| 5 | Why does Rule 5 (whitespace cleanup) come last? | Because earlier rules create extra spaces when they remove content. Cleanup last ensures the final result has no gaps. |
| 6 | Can the user override auto-generated audio text? | Yes — if the client sends an explicit `front_audio_text_1` value, the API uses it instead of generating one. |
| 7 | How do you add a new regex rule? | Add another `text = re.sub(r'pattern', 'replacement', text)` line in the function, at the appropriate position. |

---

---

## SECTION 8 — PUBLIC SHARING AND THE COPY FEATURE

---

We have arrived at the final section. Let us recall the full journey: Section 1 explained why we need a multi-user API. Section 2 set up the environment. Section 3 designed four tables with ownership, visibility, and audit columns. Section 4 organized the project files. Section 5 built Pydantic models for all entities. Section 6 implemented 21 endpoints with ownership checks and audit trails. Section 7 added regex-based audio text generation. Now, Section 8 adds the copy feature — the ability for any user to duplicate a public card set into their own account.

This section has **three parts**:
1. Why copying is needed and what exactly happens during a copy
2. The copy endpoint implementation
3. Testing the full workflow

### 8.1 — Why Copying Is Needed

Consider this scenario. User A is a Spanish teacher who has spent hours building a card set called "DELE B2 Vocabulary" with 200 perfectly crafted cards, complete with audio text and image URLs. User A marks it as public so their students can benefit.

User B, a student, finds this public card set. They want to study from it, but they also want to add their own notes, modify some translations, and remove cards they already know. If User B directly edits User A's set, that would require User B to be the owner — which they are not. And even if we allowed it, User B's changes would affect everyone else using the public set.

The solution is **copying**: User B creates a complete, independent duplicate of User A's card set. This new copy belongs to User B — they are the owner. They can edit, delete, add cards, make it private, whatever they want. User A's original set is completely unaffected.

### 8.2 — What Happens During a Copy

The copy operation is not a simple single-table insert. It involves multiple steps, and the order matters:

**Step 1:** Verify that the source card set exists and is public (or is owned by the requesting user — you can copy your own sets too).

**Step 2:** The requesting user must specify which of their own folders to place the copy into, via a `target_folder_id` parameter. We verify that this folder exists and belongs to the requesting user. This is necessary because folders are now user-owned — you cannot place a copied card set into someone else's folder.

**Step 3:** Create a new card set record with the target folder's ID as `cardfolder_id`, the source's `name` (prefixed with "Copy of " to distinguish it), and `description` — but with the requesting user's ID as `user_id` and `is_public` set to `false` (the copy starts private).

**Step 4:** Fetch all cards from the source card set.

**Step 5:** For each card, create a new card record with the same content fields (all eight: front and back text, audio text, audio URL, image URL) but with the new card set's ID as `cardset_id`. The `id`, `created_at`, `updated_at`, and `updated_by` fields are NOT copied — each new card gets a fresh ID, a fresh creation timestamp, and null audit fields (it has never been updated yet, only created).

This is a "deep copy" — the card set AND all its cards are duplicated. The original and the copy are completely independent afterward. Editing the copy does not affect the original, and vice versa.

### 8.3 — The Copy Endpoint

We add this endpoint to the `cardset_router.py` file. Here is the new endpoint to add at the bottom of the file, after the existing seven endpoints:

**Add to `routers/cardset_router.py`:**

First, add this import at the top of the file alongside the existing imports:

```python
from utils.audio_text import generate_audio_text
```

Then add the endpoint:

```python
# ──────────────────────────────────────────────────────────────────
# ENDPOINT 8: Copy a public card set into your own account
# ──────────────────────────────────────────────────────────────────
@router.post("/{cardset_id}/copy", response_model=CardsetResponse)
def copy_cardset(cardset_id: str, target_folder_id: str, x_user_id: str = Header(...)):
    verify_user(x_user_id)

    # Step 1: Fetch the source card set and verify it is accessible
    source_result = supabase.table("cardsets").select("*").eq("id", cardset_id).execute()
    if not source_result.data:
        raise HTTPException(status_code=404, detail="Card set not found")

    source = source_result.data[0]

    # Allow copy if: the set is public, OR the requester is the owner
    if not source["is_public"] and source["user_id"] != x_user_id:
        raise HTTPException(
            status_code=403,
            detail="This card set is private and you are not the owner"
        )

    # Step 2: Verify the target folder exists and belongs to the requesting user
    folder_check = supabase.table("cardfolders").select("*").eq("id", target_folder_id).execute()
    if not folder_check.data:
        raise HTTPException(status_code=404, detail="Target folder not found")
    if folder_check.data[0]["user_id"] != x_user_id:
        raise HTTPException(status_code=403, detail="You do not own the target folder")

    # Step 3: Create the new card set (owned by requesting user, private by default)
    new_cardset_data = {
        "cardfolder_id": target_folder_id,
        "user_id": x_user_id,
        "name": f"Copy of {source['name']}",
        "description": source.get("description"),
        "is_public": False
    }

    new_cardset_result = supabase.table("cardsets").insert(new_cardset_data).execute()
    if not new_cardset_result.data:
        raise HTTPException(status_code=400, detail="Failed to create card set copy")

    new_cardset = new_cardset_result.data[0]

    # Step 4: Fetch all cards from the source card set
    source_cards = supabase.table("cards").select("*").eq("cardset_id", cardset_id).execute()

    # Step 5: Duplicate each card into the new card set
    if source_cards.data:
        new_cards = []
        for card in source_cards.data:
            new_card = {
                "cardset_id": new_cardset["id"],
                "front_text_1": card.get("front_text_1"),
                "front_audio_text_1": card.get("front_audio_text_1"),
                "front_audio_1": card.get("front_audio_1"),
                "front_image": card.get("front_image"),
                "back_text_1": card.get("back_text_1"),
                "back_audio_text_1": card.get("back_audio_text_1"),
                "back_audio_1": card.get("back_audio_1"),
                "back_image": card.get("back_image"),
            }
            new_cards.append(new_card)

        # Batch insert all cards at once for efficiency
        supabase.table("cards").insert(new_cards).execute()

    return new_cardset
```

Let us walk through every detail of this endpoint.

**The URL pattern:** `@router.post("/{cardset_id}/copy")`. This means: send a POST request to `/cardsets/{cardset_id}/copy`. The `cardset_id` in the URL is the source card set you want to copy. We use POST (not GET) because this operation creates new data — it is not a read operation. The function also takes `target_folder_id` as a query parameter — the client must specify which of their own folders to place the copy into.

**Step 1 — Access verification:** We fetch the source card set and check two things. Does it exist? And is it accessible to the requesting user? A card set is accessible if it is public (`is_public` is true) OR if the requester is the owner. This means you can copy your own private sets too — which is useful for creating variations of your own work.

**Step 2 — Target folder verification:** Since folders belong to users, the copy must go into a folder that the requesting user owns. We fetch the target folder and check both that it exists and that its `user_id` matches the requesting user. This prevents someone from placing copied card sets into another user's folder structure.

**Step 3 — Create the new card set:** We build a dictionary with `target_folder_id` as the `cardfolder_id` (the copy goes into the user's chosen folder), the requesting user's ID as `user_id` (they become the owner), the name prefixed with "Copy of " (so it is distinguishable at a glance), the same description, and `is_public` set to `False` (the copy starts private — the new owner can make it public later if they wish).

**Step 4 — Fetch source cards:** We query all cards that belong to the source card set. The `.data` attribute is a list of dictionaries.

**Step 5 — Duplicate cards:** We loop through each source card and build a new card dictionary. Notice what we copy and what we DO NOT copy:

We COPY: `front_text_1`, `front_audio_text_1`, `front_audio_1`, `front_image`, `back_text_1`, `back_audio_text_1`, `back_audio_1`, `back_image`. All eight content fields are preserved exactly.

We DO NOT COPY: `id` (each new card gets a fresh UUID from the database), `cardset_id` (set to the new card set's ID, not the source's), `created_at` (set to the current moment by the database), `updated_at` (null — the new card has never been updated), `updated_by` (null — same reason).

The key design decision: we use `card.get("field_name")` instead of `card["field_name"]`. The `.get()` method returns `None` if the key does not exist, while bracket access would raise a `KeyError`. This is defensive programming — it handles edge cases where a card might not have every field populated.

**Batch insert:** Instead of inserting cards one at a time in a loop (which would make one database call per card), we collect all new cards in a list and call `supabase.table("cards").insert(new_cards).execute()` once. Supabase's `insert` method accepts a list of dictionaries and inserts them all in one operation. This is dramatically faster for large card sets — inserting 200 cards in one call instead of 200 separate calls.

**The return value:** We return the new card set record (not the cards). The client now has the ID of their copy and can use `GET /cards/cardset/{new_id}` to view the copied cards.

### 8.4 — Testing the Full Copy Workflow

Here is the complete testing sequence to verify everything works end-to-end. Use the interactive docs at `http://localhost:8000/docs`:

1. **Register two users.** POST `/users/` with `{"username": "teacher_ana", "email": "ana@example.com"}`. Copy the `id`. POST `/users/` with `{"username": "student_bob", "email": "bob@example.com"}`. Copy the `id`.

2. **Teacher creates a folder.** POST `/cardfolders/` with header `x-user-id: [teacher's ID]` and body `{"name": "Languages"}`. Copy the folder `id`.

3. **Student creates their own folder.** POST `/cardfolders/` with header `x-user-id: [student's ID]` and body `{"name": "My Studies"}`. Copy this folder `id` too — the student will need it for the copy.

4. **Teacher creates a card set.** POST `/cardsets/` with header `x-user-id: [teacher's ID]` and body `{"cardfolder_id": "[teacher's folder ID]", "name": "Spanish Basics", "is_public": true}`. Copy the card set `id`.

5. **Teacher adds cards.** POST `/cards/` with header `x-user-id: [teacher's ID]` and body `{"cardset_id": "[cardset ID]", "front_text_1": "El gato (the cat) [m.]", "back_text_1": "The cat"}`. Repeat for a few cards. Notice the `front_audio_text_1` is auto-generated as `"El gato"`.

6. **Student browses public sets.** GET `/cardsets/public` — the student can see "Spanish Basics" listed.

7. **Student copies the set into their own folder.** POST `/cardsets/[cardset ID]/copy?target_folder_id=[student's folder ID]` with header `x-user-id: [student's ID]`. The response shows a new card set called "Copy of Spanish Basics" owned by the student, inside the student's "My Studies" folder, private by default.

8. **Student views their copy.** GET `/cardsets/my` with header `x-user-id: [student's ID]` — they see "Copy of Spanish Basics" in their collection.

9. **Student edits a card in their copy.** GET `/cards/cardset/[new cardset ID]` to see all copied cards. Pick one card's ID. PUT `/cards/[card ID]` with header `x-user-id: [student's ID]` and body `{"front_text_1": "El gato gordo (the fat cat)"}`. The response shows `updated_at` with the current timestamp and `updated_by` with the student's ID. The `front_audio_text_1` is automatically regenerated as `"El gato gordo"`.

10. **Verify teacher's original is untouched.** GET `/cards/cardset/[original cardset ID]` — the teacher's cards are exactly as they were. The student's edits only affected their copy.

11. **Student tries to edit teacher's original — blocked.** PUT `/cards/[teacher's card ID]` with header `x-user-id: [student's ID]` — returns 403 "You do not own the parent card set."

### Section 8 — Review

Section 8 completes the application. The copy endpoint performs a deep copy: the user specifies a target folder they own, a new card set is created in that folder, and all cards from the source are duplicated. Content is preserved exactly; metadata (IDs, timestamps, audit fields) starts fresh. Access is controlled: only public sets (or your own sets) can be copied, and the target folder must belong to you. The batch insert ensures efficiency even for large card sets.

All eight sections are now complete.

### Section 8 — Q&A Table

| # | Question | Answer |
|---|----------|--------|
| 1 | Why use POST for the copy endpoint, not GET? | Because copying creates new data (a new card set and new cards). GET should never create data — it is for reading only. |
| 2 | What does the copied card set's name look like? | "Copy of [original name]" — e.g., "Copy of Spanish Basics." The new owner can rename it later. |
| 3 | Is the copy public or private? | Private by default (`is_public: false`). The new owner can make it public later if they wish. |
| 4 | Are card IDs preserved during copy? | No — each card gets a fresh UUID. The copy is completely independent; editing it does not affect the original. |
| 5 | Is `updated_at` copied from the source cards? | No — copied cards have `updated_at: null` because they are newly created, never updated. |
| 6 | Can you copy your own card set? | Yes — the check allows access if the set is public OR if you are the owner. This is useful for creating variations. |
| 7 | Why use `card.get("field")` instead of `card["field"]`? | `.get()` returns None if the key is missing, avoiding KeyError. Defensive programming for cards with unpopulated fields. |
| 8 | Why batch insert instead of a loop? | One database call for all cards is far faster than one call per card. Inserting 200 cards in a loop makes 200 network round trips. |

---

---

## FINAL SUMMARY — THE COMPLETE APPLICATION

---

We have built a complete multi-user FastAPI application with Supabase integration across eight sections. Here is the total inventory:

**Files created:**
- `.env` — Supabase credentials (Section 2)
- `.gitignore` — protection for secrets and cache (Section 2)
- `database.py` — Supabase client connection (Section 4)
- `main.py` — application entry point with four router includes (Section 4)
- `models/user_models.py` — user Pydantic models (Section 5)
- `models/cardfolder_models.py` — folder Pydantic models (Section 5)
- `models/cardset_models.py` — card set Pydantic models with ownership and visibility (Section 5)
- `models/card_models.py` — card Pydantic models with audit fields (Section 5)
- `routers/user_router.py` — 3 user endpoints (Section 6)
- `routers/cardfolder_router.py` — 5 folder endpoints with ownership (Section 6)
- `routers/cardset_router.py` — 8 card set endpoints including copy (Sections 6 & 8)
- `routers/card_router.py` — 6 card endpoints with audit tracking (Section 6)
- `utils/audio_text.py` — regex-based audio text generation (Section 7)

**Total endpoints: 22** (plus the root `/` health check in `main.py`).

**Multi-user features implemented:**
- User registration and lookup
- Folder ownership via `user_id` foreign key
- Card set ownership via `user_id` foreign key
- Ownership enforcement on all write operations (create, update, delete)
- Public/private visibility via `is_public` boolean
- Visibility filtering on all read operations
- Card-level audit trail via `updated_at` and `updated_by`
- Deep copy of public card sets with batch card duplication
- Simplified authentication via `x-user-id` header

**To run the application:**

```bash
cd flashcard-api
source venv/bin/activate
uvicorn main:app --reload
```

Then open `http://localhost:8000/docs` to see and test every endpoint interactively.

## Master Q&A Table

| # | Topic | Question | Answer |
|---|-------|----------|--------|
| 1 | Architecture | What are the four levels of our data hierarchy? | Users → Folders → Card Sets → Cards. Users own folders and card sets. Visibility is controlled at the card set level. |
| 2 | Architecture | How many files contain endpoint logic? | Four router files: `user_router.py`, `cardfolder_router.py`, `cardset_router.py`, `card_router.py`. |
| 3 | Database | What prevents orphaned records when a parent is deleted? | ON DELETE CASCADE on foreign keys — deleting a parent auto-deletes all children. |
| 4 | Database | Why does `updated_by` use SET NULL instead of CASCADE? | To preserve cards even when the user who edited them is deleted — only the reference clears, not the data. |
| 5 | Ownership | How does the API know who is making a request? | Via the `x-user-id` HTTP header. Production systems would use JWT or OAuth instead. |
| 6 | Ownership | What happens if User B tries to edit User A's card set? | The API returns 403 Forbidden — "You do not own this card set." |
| 7 | Visibility | What does `is_public: false` mean for a card set? | Only the owner can see, edit, or access the card set and its cards. All other users get 403. |
| 8 | Visibility | How do cards inherit visibility? | From their parent card set. If the card set is private, all its cards are inaccessible to non-owners. |
| 9 | Audit | When are `updated_at` and `updated_by` set? | Every time a card is updated via PUT. They are set by the API, never by the client. |
| 10 | Audit | What is `updated_at` for a brand-new card? | Null — the card has been created but never updated. |
| 11 | Copy | What happens when you copy a card set? | A new card set is created (owned by you, private) and all source cards are duplicated with fresh IDs and timestamps. |
| 12 | Copy | Does editing a copied card affect the original? | No — the copy is completely independent. Editing it has zero effect on the original. |
| 13 | Validation | What library provides automatic request validation? | Pydantic, via BaseModel subclasses used as function parameter types. |
| 14 | Updates | What prevents data loss during partial updates? | `model_dump(exclude_unset=True)` — only includes fields the client explicitly sent. |
| 15 | Audio | How are audio text fields populated? | Automatically via `generate_audio_text()` if the client provides display text but not audio text. |
