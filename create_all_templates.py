import os

# Get the current directory
base_dir = os.path.dirname(os.path.abspath(__file__))
templates_dir = os.path.join(base_dir, 'templates')

# Create all template directories
subdirs = ['adoption', 'lost_found', 'education', 'dog_profile', 'auth']
for subdir in subdirs:
    os.makedirs(os.path.join(templates_dir, subdir), exist_ok=True)

# Template content for each file
templates = {
    # Root templates
    'base.html': '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{% block title %}FurEverSafe - Responsible Dog Ownership{% endblock %}</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css">
</head>
<body>
    <nav class="navbar navbar-expand-lg navbar-dark bg-primary">
        <div class="container">
            <a class="navbar-brand" href="{{ url_for('index') }}">
                <i class="fas fa-paw"></i> FurEverSafe
            </a>
            <button class="navbar-toggler" type="button" data-bs-toggle="collapse" data-bs-target="#navbarNav">
                <span class="navbar-toggler-icon"></span>
            </button>
            <div class="collapse navbar-collapse" id="navbarNav">
                <ul class="navbar-nav me-auto">
                    <li class="nav-item"><a class="nav-link" href="{{ url_for('index') }}">Home</a></li>
                    <li class="nav-item"><a class="nav-link" href="{{ url_for('adoption_listings') }}">Adopt</a></li>
                    <li class="nav-item"><a class="nav-link" href="{{ url_for('lost_found_reports') }}">Lost & Found</a></li>
                    <li class="nav-item"><a class="nav-link" href="{{ url_for('education_resources') }}">Education</a></li>
                    {% if current_user.is_authenticated %}
                    <li class="nav-item"><a class="nav-link" href="{{ url_for('dashboard') }}">Dashboard</a></li>
                    {% endif %}
                </ul>
                <ul class="navbar-nav">
                    {% if current_user.is_authenticated %}
                    <li class="nav-item dropdown">
                        <a class="nav-link dropdown-toggle" href="#" data-bs-toggle="dropdown">
                            <i class="fas fa-user"></i> {{ current_user.username }}
                        </a>
                        <ul class="dropdown-menu">
                            <li><a class="dropdown-item" href="{{ url_for('dashboard') }}">Dashboard</a></li>
                            <li><hr class="dropdown-divider"></li>
                            <li><a class="dropdown-item" href="{{ url_for('logout') }}">Logout</a></li>
                        </ul>
                    </li>
                    {% else %}
                    <li class="nav-item"><a class="nav-link" href="{{ url_for('login') }}">Login</a></li>
                    <li class="nav-item"><a class="nav-link" href="{{ url_for('register') }}">Register</a></li>
                    {% endif %}
                </ul>
            </div>
        </div>
    </nav>

    <main class="container mt-4">
        {% with messages = get_flashed_messages(with_categories=true) %}
            {% if messages %}
                {% for category, message in messages %}
                    <div class="alert alert-{{ category }} alert-dismissible fade show">
                        {{ message }}
                        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
                    </div>
                {% endfor %}
            {% endif %}
        {% endwith %}
        
        {% block content %}{% endblock %}
    </main>

    <footer class="bg-dark text-light mt-5 py-4">
        <div class="container text-center">
            <p>&copy; 2024 FurEverSafe. All rights reserved.</p>
        </div>
    </footer>

    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/js/bootstrap.bundle.min.js"></script>
</body>
</html>''',

    'index.html': '''{% extends "base.html" %}
{% block title %}Home - FurEverSafe{% endblock %}
{% block content %}
<div class="bg-light p-5 rounded-lg text-center">
    <h1 class="display-4">Welcome to FurEverSafe</h1>
    <p class="lead">Your complete platform for responsible dog ownership and animal welfare</p>
    <a href="{{ url_for('adoption_listings') }}" class="btn btn-primary btn-lg">Adopt a Dog</a>
    <a href="{{ url_for('register') }}" class="btn btn-success btn-lg">Get Started</a>
</div>
{% endblock %}''',

    'dashboard.html': '''{% extends "base.html" %}
{% block title %}Dashboard - FurEverSafe{% endblock %}
{% block content %}
<h2>Welcome back, {{ current_user.username }}!</h2>
<div class="row mt-4">
    <div class="col-md-6">
        <div class="card">
            <div class="card-header bg-primary text-white">
                <h5>Your Dogs</h5>
            </div>
            <div class="card-body">
                {% if dogs %}
                    {% for dog in dogs %}
                        <a href="{{ url_for('view_dog', dog_id=dog.id) }}" class="list-group-item list-group-item-action">
                            {{ dog.name }} - {{ dog.breed }}
                        </a>
                    {% endfor %}
                {% else %}
                    <p>No dogs added yet.</p>
                    <a href="{{ url_for('create_dog') }}" class="btn btn-primary">Add Your First Dog</a>
                {% endif %}
            </div>
        </div>
    </div>
    <div class="col-md-6">
        <div class="card">
            <div class="card-header bg-success text-white">
                <h5>Quick Actions</h5>
            </div>
            <div class="card-body">
                <a href="{{ url_for('create_dog') }}" class="btn btn-outline-primary btn-sm">Add Dog</a>
                <a href="{{ url_for('report_lost_found') }}" class="btn btn-outline-danger btn-sm">Report Lost/Found</a>
            </div>
        </div>
    </div>
</div>
{% endblock %}''',

    # Lost and Found templates
    'lost_found/reports.html': '''{% extends "base.html" %}
{% block title %}Lost & Found - FurEverSafe{% endblock %}
{% block content %}
<h2>Lost and Found Reports</h2>
<a href="{{ url_for('report_lost_found') }}" class="btn btn-danger mb-3">Report Lost/Found Dog</a>

<div class="row">
    {% for report in reports.items %}
    <div class="col-md-6 mb-3">
        <div class="card">
            <div class="card-header {% if report.type == 'lost' %}bg-danger{% else %}bg-success{% endif %} text-white">
                {{ 'Lost Dog' if report.type == 'lost' else 'Found Dog' }}
            </div>
            <div class="card-body">
                <h5>{{ report.dog_name or 'Unknown Name' }}</h5>
                <p><strong>Location:</strong> {{ report.location }}</p>
                <p><strong>Date:</strong> {{ report.date_seen.strftime('%Y-%m-%d') }}</p>
                <a href="{{ url_for('view_report', report_id=report.id) }}" class="btn btn-sm btn-primary">View Details</a>
            </div>
        </div>
    </div>
    {% else %}
    <div class="col">
        <div class="alert alert-info">No reports found.</div>
    </div>
    {% endfor %}
</div>
{% endblock %}''',

    'lost_found/create.html': '''{% extends "base.html" %}
{% block title %}Report Lost/Found - FurEverSafe{% endblock %}
{% block content %}
<h2>Report Lost or Found Dog</h2>
<form method="POST" enctype="multipart/form-data">
    {{ form.hidden_tag() }}
    <div class="mb-3">{{ form.type.label }} {{ form.type(class="form-select") }}</div>
    <div class="mb-3">{{ form.dog_name.label }} {{ form.dog_name(class="form-control") }}</div>
    <div class="mb-3">{{ form.breed.label }} {{ form.breed(class="form-control") }}</div>
    <div class="mb-3">{{ form.color.label }} {{ form.color(class="form-control") }}</div>
    <div class="mb-3">{{ form.location.label }} {{ form.location(class="form-control") }}</div>
    <div class="mb-3">{{ form.date_seen.label }} {{ form.date_seen(class="form-control", type="datetime-local") }}</div>
    <div class="mb-3">{{ form.description.label }} {{ form.description(class="form-control", rows=4) }}</div>
    <div class="mb-3">{{ form.contact_info.label }} {{ form.contact_info(class="form-control") }}</div>
    <div class="mb-3">{{ form.photo.label }} {{ form.photo(class="form-control") }}</div>
    <button type="submit" class="btn btn-primary">Submit Report</button>
</form>
{% endblock %}''',

    'lost_found/details.html': '''{% extends "base.html" %}
{% block title %}Report Details - FurEverSafe{% endblock %}
{% block content %}
<h2>{{ 'Lost Dog Report' if report.type == 'lost' else 'Found Dog Report' }}</h2>
<div class="card">
    <div class="card-body">
        <p><strong>Dog Name:</strong> {{ report.dog_name or 'Unknown' }}</p>
        <p><strong>Breed:</strong> {{ report.breed or 'Unknown' }}</p>
        <p><strong>Color:</strong> {{ report.color or 'Unknown' }}</p>
        <p><strong>Location:</strong> {{ report.location }}</p>
        <p><strong>Date Seen:</strong> {{ report.date_seen.strftime('%Y-%m-%d %H:%M') }}</p>
        <p><strong>Description:</strong> {{ report.description }}</p>
        <p><strong>Contact:</strong> {{ report.contact_info or 'Not provided' }}</p>
    </div>
</div>
{% endblock %}''',

    # Adoption templates
    'adoption/listings.html': '''{% extends "base.html" %}
{% block title %}Adopt a Dog - FurEverSafe{% endblock %}
{% block content %}
<h2>Dogs Available for Adoption</h2>
<div class="row">
    {% for listing in listings.items %}
    <div class="col-md-4 mb-3">
        <div class="card h-100">
            {% if listing.photo %}
            <img src="{{ url_for('static', filename='uploads/' + listing.photo) }}" class="card-img-top" style="height: 200px; object-fit: cover;">
            {% endif %}
            <div class="card-body">
                <h5 class="card-title">{{ listing.dog_name }}</h5>
                <p class="card-text">{{ listing.breed }} - {{ listing.age }} years</p>
                <a href="{{ url_for('view_adoption_listing', listing_id=listing.id) }}" class="btn btn-primary">View Details</a>
            </div>
        </div>
    </div>
    {% endfor %}
</div>
{% endblock %}''',

    'adoption/details.html': '''{% extends "base.html" %}
{% block title %}Adoption Details - FurEverSafe{% endblock %}
{% block content %}
<h2>{{ listing.dog_name }}</h2>
<div class="card">
    <div class="card-body">
        <p><strong>Breed:</strong> {{ listing.breed }}</p>
        <p><strong>Age:</strong> {{ listing.age }} years</p>
        <p><strong>Gender:</strong> {{ listing.gender }}</p>
        <p><strong>Size:</strong> {{ listing.size }}</p>
        <p><strong>Description:</strong> {{ listing.description }}</p>
        <a href="{{ url_for('apply_for_adoption', listing_id=listing.id) }}" class="btn btn-success">Apply for Adoption</a>
    </div>
</div>
{% endblock %}''',

    'adoption/create.html': '''{% extends "base.html" %}
{% block title %}Create Listing - FurEverSafe{% endblock %}
{% block content %}
<h2>Create Adoption Listing</h2>
<form method="POST" enctype="multipart/form-data">
    {{ form.hidden_tag() }}
    <div class="mb-3">{{ form.dog_name.label }} {{ form.dog_name(class="form-control") }}</div>
    <div class="mb-3">{{ form.breed.label }} {{ form.breed(class="form-control") }}</div>
    <div class="mb-3">{{ form.age.label }} {{ form.age(class="form-control") }}</div>
    <div class="mb-3">{{ form.gender.label }} {{ form.gender(class="form-select") }}</div>
    <div class="mb-3">{{ form.size.label }} {{ form.size(class="form-select") }}</div>
    <div class="mb-3">{{ form.description.label }} {{ form.description(class="form-control", rows=5) }}</div>
    <div class="mb-3">{{ form.photo.label }} {{ form.photo(class="form-control") }}</div>
    <button type="submit" class="btn btn-primary">Create Listing</button>
</form>
{% endblock %}''',

    'adoption/apply.html': '''{% extends "base.html" %}
{% block title %}Apply for Adoption - FurEverSafe{% endblock %}
{% block content %}
<h2>Apply for {{ listing.dog_name }}</h2>
<form method="POST">
    {{ form.hidden_tag() }}
    <div class="mb-3">{{ form.message.label }} {{ form.message(class="form-control", rows=5) }}</div>
    <button type="submit" class="btn btn-success">Submit Application</button>
</form>
{% endblock %}''',

    'adoption/applications.html': '''{% extends "base.html" %}
{% block title %}Applications - FurEverSafe{% endblock %}
{% block content %}
<h2>Adoption Applications</h2>
{% for app in applications %}
<div class="card mb-3">
    <div class="card-body">
        <h5>{{ app.listing.dog_name }}</h5>
        <p>Status: {{ app.status }}</p>
        <p>{{ app.message }}</p>
    </div>
</div>
{% endfor %}
{% endblock %}''',

    # Education templates
    'education/resources.html': '''{% extends "base.html" %}
{% block title %}Education - FurEverSafe{% endblock %}
{% block content %}
<h2>Educational Resources</h2>
<div class="row">
    {% for resource in resources.items %}
    <div class="col-md-4 mb-3">
        <div class="card">
            <div class="card-body">
                <h5 class="card-title">{{ resource.title }}</h5>
                <p class="card-text">{{ resource.content[:100] }}...</p>
                <a href="{{ url_for('view_article', resource_id=resource.id) }}" class="btn btn-primary">Read More</a>
            </div>
        </div>
    </div>
    {% endfor %}
</div>
{% endblock %}''',

    'education/article.html': '''{% extends "base.html" %}
{% block title %}{{ resource.title }}{% endblock %}
{% block content %}
<h2>{{ resource.title }}</h2>
<p class="text-muted">Category: {{ resource.category }} | Views: {{ resource.views }}</p>
<div class="mt-4">
    {{ resource.content|safe }}
</div>
{% endblock %}''',

    'education/create.html': '''{% extends "base.html" %}
{% block title %}Create Resource - FurEverSafe{% endblock %}
{% block content %}
<h2>Create Educational Resource</h2>
<form method="POST" enctype="multipart/form-data">
    {{ form.hidden_tag() }}
    <div class="mb-3">{{ form.title.label }} {{ form.title(class="form-control") }}</div>
    <div class="mb-3">{{ form.category.label }} {{ form.category(class="form-select") }}</div>
    <div class="mb-3">{{ form.content.label }} {{ form.content(class="form-control", rows=10) }}</div>
    <div class="mb-3">{{ form.author.label }} {{ form.author(class="form-control") }}</div>
    <div class="mb-3">{{ form.thumbnail.label }} {{ form.thumbnail(class="form-control") }}</div>
    <button type="submit" class="btn btn-primary">Create Resource</button>
</form>
{% endblock %}''',

    # Dog Profile templates
    'dog_profile/create.html': '''{% extends "base.html" %}
{% block title %}Add Dog - FurEverSafe{% endblock %}
{% block content %}
<h2>Add New Dog</h2>
<form method="POST" enctype="multipart/form-data">
    {{ form.hidden_tag() }}
    <div class="mb-3">{{ form.name.label }} {{ form.name(class="form-control") }}</div>
    <div class="mb-3">{{ form.breed.label }} {{ form.breed(class="form-control") }}</div>
    <div class="mb-3">{{ form.age.label }} {{ form.age(class="form-control") }}</div>
    <div class="mb-3">{{ form.weight.label }} {{ form.weight(class="form-control") }}</div>
    <div class="mb-3">{{ form.microchip_id.label }} {{ form.microchip_id(class="form-control") }}</div>
    <div class="mb-3">{{ form.photo.label }} {{ form.photo(class="form-control") }}</div>
    <button type="submit" class="btn btn-primary">Add Dog</button>
</form>
{% endblock %}''',

    'dog_profile/view.html': '''{% extends "base.html" %}
{% block title %}{{ dog.name }} - FurEverSafe{% endblock %}
{% block content %}
<h2>{{ dog.name }}</h2>
<div class="card">
    <div class="card-body">
        <p><strong>Breed:</strong> {{ dog.breed }}</p>
        <p><strong>Age:</strong> {{ dog.age }} years</p>
        <p><strong>Weight:</strong> {{ dog.weight }} kg</p>
        <p><strong>Microchip ID:</strong> {{ dog.microchip_id or 'Not registered' }}</p>
        <a href="{{ url_for('edit_dog', dog_id=dog.id) }}" class="btn btn-warning">Edit</a>
    </div>
</div>
{% endblock %}''',

    'dog_profile/edit.html': '''{% extends "base.html" %}
{% block title %}Edit {{ dog.name }}{% endblock %}
{% block content %}
<h2>Edit {{ dog.name }}</h2>
<form method="POST" enctype="multipart/form-data">
    {{ form.hidden_tag() }}
    <div class="mb-3">{{ form.name.label }} {{ form.name(class="form-control") }}</div>
    <div class="mb-3">{{ form.breed.label }} {{ form.breed(class="form-control") }}</div>
    <div class="mb-3">{{ form.age.label }} {{ form.age(class="form-control") }}</div>
    <div class="mb-3">{{ form.weight.label }} {{ form.weight(class="form-control") }}</div>
    <div class="mb-3">{{ form.microchip_id.label }} {{ form.microchip_id(class="form-control") }}</div>
    <div class="mb-3">{{ form.photo.label }} {{ form.photo(class="form-control") }}</div>
    <button type="submit" class="btn btn-primary">Update Dog</button>
</form>
{% endblock %}''',

    # Auth templates
    'auth/login.html': '''{% extends "base.html" %}
{% block title %}Login - FurEverSafe{% endblock %}
{% block content %}
<div class="row justify-content-center">
    <div class="col-md-6">
        <div class="card">
            <div class="card-header bg-primary text-white">Login</div>
            <div class="card-body">
                <form method="POST">
                    {{ form.hidden_tag() }}
                    <div class="mb-3">{{ form.email.label }} {{ form.email(class="form-control") }}</div>
                    <div class="mb-3">{{ form.password.label }} {{ form.password(class="form-control") }}</div>
                    <button type="submit" class="btn btn-primary">Login</button>
                </form>
            </div>
        </div>
    </div>
</div>
{% endblock %}''',

    'auth/register.html': '''{% extends "base.html" %}
{% block title %}Register - FurEverSafe{% endblock %}
{% block content %}
<div class="row justify-content-center">
    <div class="col-md-6">
        <div class="card">
            <div class="card-header bg-primary text-white">Register</div>
            <div class="card-body">
                <form method="POST">
                    {{ form.hidden_tag() }}
                    <div class="mb-3">{{ form.username.label }} {{ form.username(class="form-control") }}</div>
                    <div class="mb-3">{{ form.email.label }} {{ form.email(class="form-control") }}</div>
                    <div class="mb-3">{{ form.user_type.label }} {{ form.user_type(class="form-select") }}</div>
                    <div class="mb-3">{{ form.password.label }} {{ form.password(class="form-control") }}</div>
                    <div class="mb-3">{{ form.confirm_password.label }} {{ form.confirm_password(class="form-control") }}</div>
                    <button type="submit" class="btn btn-primary">Register</button>
                </form>
            </div>
        </div>
    </div>
</div>
{% endblock %}'''
}

# Create all template files
for filepath, content in templates.items():
    full_path = os.path.join(templates_dir, filepath)
    with open(full_path, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f"Created: {full_path}")

print("\n✅ All template files have been created successfully!")
print(f"Templates directory: {templates_dir}")
print("\nNow run: python app.py")