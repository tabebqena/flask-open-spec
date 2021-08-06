This library provide command line to facilitate craeting Open API specifications of flask apps with marshmallow schemas.
<br>
## Installation:
<br>
<br>
    pip install git+[https://gitlab.com/tabebqena/marshmaloow-stubplugin.git](https://gitlab.com/tabebqena/marshmaloow-stubplugin.git)

<br>
<br>
**Usage:**

<br>
    from stub\_plugin import add\_cli
    from flask import Flask

    app = Flask(\_\_name\_\_)
    add\_cli(app)
<br>
## Commands

### init

From the command line :

```
flask oas init
```
<br>
This command will create many files and stubs, in the `./oas` dir.

Created Files:

* ./oas/generated/info.yaml

> stub to provide the info of the openapi

<span class="colour" style="color:rgb(103, 150, 230)">-</span><span class="colour" style="color:rgb(212, 212, 212)"> ./oas/generated/paths\_list.yaml</span>

> extracts of all paths registered in the flask app

<span class="colour" style="color:rgb(103, 150, 230)">-</span><span class="colour" style="color:rgb(212, 212, 212)"> ./oas/generated/parameters.yaml</span>

> extracts of all path parameters registered in the flask app.
> This parameters are extracted from routes ie:. /pets/<pet\_id>

<span class="colour" style="color:rgb(103, 150, 230)">-</span><span class="colour" style="color:rgb(212, 212, 212)"> ./oas/generated/request\_body.yaml</span>

> This is stub, You shoud define here all your marshmallow schemas that are used in the request body (form , json, content)

<span class="colour" style="color:rgb(103, 150, 230)">-</span><span class="colour" style="color:rgb(212, 212, 212)"> ./oas/generated/responses\_schemas.yaml</span>

> This is stub, You shoud define here all your marshmallow schemas that are used in the responses

<span class="colour" style="color:rgb(103, 150, 230)">-</span><span class="colour" style="color:rgb(212, 212, 212)"> ./oas/generated/servers.yaml</span>

> This is stub, You **MAY** define here your servers. If you have more than one

<span class="colour" style="color:rgb(103, 150, 230)">-</span><span class="colour" style="color:rgb(212, 212, 212)"> ./oas/generated/tags.yaml</span>

> This is stub, You **MAY** define here your tags.

<span class="colour" style="color:rgb(103, 150, 230)">-</span><span class="colour" style="color:rgb(212, 212, 212)"> ./oas/generated/security.yaml</span>

> This is stub, You **MAY** define here your security schemas.

<span class="colour" style="color:rgb(103, 150, 230)">-</span><span class="colour" style="color:rgb(212, 212, 212)"> ./oas/override\_oas.yaml</span>

> If you want to override any data extracted from the command build. You can write it here.
> You should strictly follow the same data schema.

### **Build**
<br>
```
 flask oas build
```
<br>
<br>
This command will build and construct the `final_oas.yaml` file.

You can use this file to get the json data of openapi spec.
<br>
### clean
<br>
<br>
    flask oas clean

This will move all files from \`./oas/generated\` to \`./oas/cache\`