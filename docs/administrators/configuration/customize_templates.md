# Template Customization
 
The researcher interface has a minimal header and footer without account options such as a
logout button, because your Django project handles authentication (see
[User Authentication](user_authentication.md)). To add your own branding or account options,
override DDM's base template using Django's template inheritance.
 
## Override the Header and Footer
 
1. In one of your apps, create the file `your_app/templates/ddm_core/base.html`.
2. Extend DDM's base template and override the blocks you want to change:
```django
    {% extends "ddm_core/base.html" %}
 
    {% block extrahead %}
        {{ block.super }}
        <!-- Custom CSS, favicon, etc. -->
    {% endblock %}
 
    {% block header %}
    <div>
        <!-- Your header HTML -->
        <form method="post" action="{% url 'ddm_logout' %}">
            {% csrf_token %}
            <button type="submit">Log out</button>
        </form>
    </div>
    {% endblock %}
 
    {% block footer %}
    <div>
        <!-- Your footer HTML -->
    </div>
    {% endblock %}
```
 
Use `{{ block.super }}` to keep DDM's default content of a block and add to it. Django's
logout view only accepts POST requests, so use a form for the logout button, not a link.
 
3. Make sure your app comes **before** `ddm.core` in `INSTALLED_APPS`.

!!! warning "Overrides are ignored if the app order is wrong"
 
    Django's template loader searches `INSTALLED_APPS` in order and uses the first match. If
    your app comes after `ddm.core`, Django uses DDM's own `ddm_core/base.html` and silently
    ignores your override. See
    [Installation Guide → Update settings.py](../installation.md#update-settingspy).
 
## Available Blocks
 
`ddm_core/base.html` defines the following blocks:
 
| Block                  | Contains                                                                   |
|------------------------|----------------------------------------------------------------------------|
| `extrahead`            | Extra content for `<head>`, such as CSS or a favicon.                      |
| `page_title`           | The page title.                                                            |
| `header`               | The page header.                                                           |
| `main_heading_wrapper` | The page heading; wraps `main_heading` and `sub_heading`.                  |
| `pre_footer`           | The area above the footer; wraps `pre_footer_left` and `pre_footer_right`. |
| `footer`               | The page footer.                                                           |
| `scripts`              | Extra `<script>` tags at the end of `<body>`.                              |
