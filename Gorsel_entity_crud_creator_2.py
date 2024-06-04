import os
import glob
import re

MainControllerString = '''using System;
using System.Collections.Generic;
using System.Linq;
using System.Web;
using System.Web.Mvc;
using {{{WebApplication}}}.Models.Entity;

namespace {{{WebApplication}}}.Controllers
{
    public class MainController : Controller
    {
        public ActionResult Index()
        {
            return View();
        }
    }
}'''

ControllerString = '''using System;
using System.Collections.Generic;
using System.Linq;
using System.Web;
using System.Web.Mvc;
using {{{WebApplication}}}.Models.Entity;

namespace {{{WebApplication}}}.Controllers
{
    public class {{{NAME}}}Controller : Controller
    {
        {{{ENTITY}}} db = new {{{ENTITY}}}();
        // GET: {{{NAME}}}
        public ActionResult Index()
        {
            var model = db.{{{NAME}}}.ToList();
            return View(model);
        }
        public ActionResult Insert()
        {{{{ITEMS}}}
            return View();
        }
        public ActionResult Insert2({{{NAME}}} p)
        {
            if (ModelState.IsValid)
			{
                db.{{{NAME}}}.Add(p);
                db.SaveChanges();
                return RedirectToAction("Index");
			}
            else
			{
                return RedirectToAction("Insert");
            }
        }

        public ActionResult Update({{{NAME}}} p)
        {{{{ITEMS}}}

            var model = db.{{{NAME}}}.Find(p.Id);
            if (model == null)
                return HttpNotFound();
            return View(model);
        }

        public ActionResult Update2({{{NAME}}} p)
        {
            if (ModelState.IsValid)
            {
                db.Entry(p).State = System.Data.Entity.EntityState.Modified;
                db.SaveChanges();
                return RedirectToAction("Index");
            }
            else
            {
                return RedirectToAction("Update");
            }
        }

        public ActionResult Delete({{{NAME}}} p)
        {
            var model = db.{{{NAME}}}.Find(p.Id);
            if (model == null)
                return HttpNotFound();
            return View(model);
        }

        public ActionResult Delete2({{{NAME}}} p)
        {
            if (ModelState.IsValid)
            {
                db.Entry(p).State = System.Data.Entity.EntityState.Deleted;
                db.SaveChanges();
                return RedirectToAction("Index");
            }
            else
            {
                return RedirectToAction("Delete");
            }
        }
    }
}'''

ControllerStringInsertItems = '''
            List<Tb{{{Item}}}> {{{Item}}} = db.Tb{{{Item}}}.ToList();
            ViewBag.{{{Item}}} = new SelectList({{{Item}}}, "Id", "{{{Item}}}");'''

DeleteString = '''@model {{{WebApplication}}}.Models.Entity.{{{NAME}}}
@{
    ViewBag.Title = "Delete";
    Layout = "~/Views/Shared/_Layout.cshtml";
}

<div class="container">
    <form action="/{{{NAME}}}/Delete2">
        @Html.HiddenFor(x => x.Id){{{ITEMS}}}
        <div class="form-group row">
            <button class="btn btn-danger">Delete Info</button>
        </div>
    </form>
</div>

<a class="btn btn-primary" href="/{{{NAME}}}/Index">Back</a>'''

DeleteItemString = '''
        <div class="form-group row">
            <label for="InputSmall" class="col-md-2 form-control-label">{{{Item}}}:</label>
            @Html.DisplayFor(x => x.{{{Item}}}, new { @class = "form-control form-control-sm" })
        </div>'''

DeleteItemString2 = '''
        <div class="form-group row">
            <label for="InputSmall" class="col-md-2 form-control-label">{{{Item}}}:</label>
            @Model.{{{Item}}}.Value.ToShortDateString()
        </div>'''

DeleteItemString3 = '''
        <div class="form-group row">
            <label for="InputSmall" class="col-md-2 form-control-label">{{{Item}}}:</label>
            @Html.DisplayFor(x => x.Tb{{{Item}}}.{{{Item}}}, new { @class = "form-control form-control-sm" })
        </div>'''

IndexString = '''@model List<{{{WebApplication}}}.Models.Entity.{{{NAME}}}>
@{
    ViewBag.Title = "Index";
    Layout = "~/Views/Shared/_Layout.cshtml";
}

<table class="table table-bordered">
    <thead>
        <tr>{{{ITEMS1}}}
        </tr>
    </thead>
    <tbody>
        @foreach (var item in Model)
			{
        <tr>{{{ITEMS2}}}
            <td><a href="/{{{NAME}}}/Update/@item.Id" class="btn btn-warning">Update</a></td>
            <td><a href="/{{{NAME}}}/Delete/@item.Id" class="btn btn-danger">Delete</a></td>
        </tr>
			}
    </tbody>
</table>

<a class="btn btn-success" href="/{{{NAME}}}/Insert">Insert</a>
<a class="btn btn-primary" href="/Main/Index">Back</a>'''

IndexItem1String = '''
            <td>{{{Item}}}</td>'''

IndexItem2String = '''
            <td>@item.{{{Item}}}</td>'''

InsertString = '''@model {{{WebApplication}}}.Models.Entity.{{{NAME}}}
@{
    ViewBag.Title = "Insert";
    Layout = "~/Views/Shared/_Layout.cshtml";
}

<div class="container">
    <form action="/{{{NAME}}}/Insert2/">{{{ITEMS}}}
        <div class="form-group row">
            <button class="btn btn-success">Insert Info</button>
        </div>
    </form>
</div>

<a class="btn btn-primary" href="/{{{NAME}}}/Index">Back</a>'''

InsertItemString = '''
        <div class="form-group row">
            <label for="InputSmall" class="col-md-2 form-control-label">{{{Item}}}:</label>
            <input type="text" name="{{{Item}}}" class="" />
        </div>'''

InsertItemString2 = '''
        <div class="form-group row">
            <label for="InputSmall" class="col-md-2 form-control-label">{{{Item}}}:</label>
            <div class="col-md-10">
                @Html.DropDownListFor(x => x.{{{Item}}}Id, ViewBag.{{{Item}}} as SelectList, "--Select--", new { @class = "form-control col-md-6" })
            </div>
        </div>'''

InsertItemString3 = '''
        <div class="form-group row">
            <label for="InputSmall" class="col-md-2 form-control-label">{{{Item}}}:</label>
            <input type="date" name="{{{Item}}}" class="" />
        </div>'''

UpdateString = '''@model {{{WebApplication}}}.Models.Entity.{{{NAME}}}
@{
    ViewBag.Title = "Update";
    Layout = "~/Views/Shared/_Layout.cshtml";
}

<div class="container">
    <form action="/{{{NAME}}}/Update2">
        @Html.HiddenFor(x => x.Id){{{ITEMS}}}
        <div class="form-group row">
            <button class="btn btn-warning">Update Info</button>
        </div>
    </form>
</div>

<a class="btn btn-primary" href="/{{{NAME}}}/Index">Back</a>'''

UpdateItemString = '''
        <div class="form-group row">
            <label for="InputSmall" class="col-md-2 form-control-label">{{{Item}}}:</label>
            @Html.TextBoxFor(x => x.{{{Item}}}, new { @class = "form-control form-control-sm" })
        </div>'''

UpdateItemString2 = '''
        <div class="form-group row">
            <label for="InputSmall" class="col-md-2 form-control-label">{{{Item}}}:</label>
            <div class="col-md-10">
                @Html.DropDownListFor(x => x.{{{Item}}}Id, ViewBag.{{{Item}}} as SelectList, "--Select--", new { @class = "form-control col-md-6" })
            </div>
        </div>'''

UpdateItemString3 = '''
        <div class="form-group row">
            <label for="InputSmall" class="col-md-2 form-control-label">{{{Item}}}:</label>
            <input type="date" name="{{{Item}}}" class="form-control col-md-6" value=@Model.{{{Item}}} />
        </div>'''

SharedLayoutString = '''<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>@ViewBag.Title - My ASP.NET Application</title>
    <link href="~/Content/Site.css" rel="stylesheet" type="text/css" />
    <link href="~/Content/bootstrap.min.css" rel="stylesheet" type="text/css" />
    <script src="~/Scripts/modernizr-2.8.3.js"></script>
</head>
<body>
    <div class="navbar navbar-inverse navbar-fixed-top">
        <div class="container">
            <div class="navbar-header">
                <button type="button" class="navbar-toggle" data-toggle="collapse" data-target=".navbar-collapse">
                    <span class="icon-bar"></span>
                    <span class="icon-bar"></span>
                    <span class="icon-bar"></span>
                </button>
                @Html.ActionLink("Application name", "Index", "Home", new { area = "" }, new { @class = "navbar-brand" })
            </div>
            <div class="navbar-collapse collapse">
                <ul class="nav navbar-nav">
                </ul>
            </div>
        </div>
    </div>

    <div class="container body-content">
        @RenderBody()
        <hr />
        <footer>
            <p>&copy; @DateTime.Now.Year - My ASP.NET Application</p>
        </footer>
    </div>

    <script src="~/Scripts/jquery-3.4.1.min.js"></script>
    <script src="~/Scripts/bootstrap.min.js"></script>
</body>
</html>'''

MainIndexString = '''@{
    ViewBag.Title = "Index";
    Layout = "~/Views/Shared/_Layout.cshtml";
}
{{{ITEMS}}}'''

MainIndexStringItem = '''
<a class="btn btn-primary" href="/{{{Item}}}/Index">{{{Item}}}</a>'''

def create_main_controller():
    file_path = os.path.join(controllers_path, "MainController.cs")
    with open(file_path, 'w') as file:
        file.write(
            MainControllerString.replace("{{{WebApplication}}}", project_name)
        )

def create_controller():
    items_string = ""
    for match in matches:
        if "Id" == match:
            continue
        if match.endswith("Id"):
            items_string += ControllerStringInsertItems.replace("{{{Item}}}", match[:-2])
    
    file_path = os.path.join(controllers_path, cs_file.split("\\")[-1][:-3] + "Controller.cs")
    with open(file_path, 'w') as file:
        file.write(
            ControllerString.replace("{{{ITEMS}}}", items_string).replace("{{{NAME}}}", table_name).replace("{{{WebApplication}}}", project_name).replace("{{{ENTITY}}}", EntityName)
        )

def create_delete():
    items_string = ""
    for match in matches:
        if "Id" == match:
            continue
        if match.endswith("Id"):
            items_string += DeleteItemString3.replace("{{{Item}}}", match[:-2])
        elif "date" in match.lower():
            items_string += DeleteItemString2.replace("{{{Item}}}", match)
        else:
            items_string += DeleteItemString.replace("{{{Item}}}", match)
    
    file_path = os.path.join(table_folder, "Delete.cshtml")
    with open(file_path, 'w') as file:
        file.write(
            DeleteString.replace("{{{NAME}}}", table_name).replace("{{{ITEMS}}}", items_string).replace("{{{WebApplication}}}", project_name)
        )

def create_index():
    items_string = ""
    items2_string = ""
    for match in matches:
        if match != "Id" and match.endswith("Id"):
            items_string += IndexItem1String.replace("{{{Item}}}", match[:-2])
            items2_string += IndexItem2String.replace("{{{Item}}}", f"Tb{match[:-2]}.{match[:-2]}")
        elif "date" in match.lower():
            items_string += IndexItem1String.replace("{{{Item}}}", match)
            items2_string += IndexItem2String.replace("{{{Item}}}", f"{match}.Value.ToShortDateString()")
        else:
            items_string += IndexItem1String.replace("{{{Item}}}", match)
            items2_string += IndexItem2String.replace("{{{Item}}}", match)
    
    file_path = os.path.join(table_folder, "Index.cshtml")
    with open(file_path, 'w') as file:
        file.write(
            IndexString.replace("{{{NAME}}}", table_name).replace("{{{ITEMS1}}}", items_string).replace("{{{ITEMS2}}}", items2_string).replace("{{{WebApplication}}}", project_name)
        )

def create_insert():
    items_string = ""
    for match in matches:
        if "Id" == match:
            continue
        if match.endswith("Id"):
            items_string += InsertItemString2.replace("{{{Item}}}", match[:-2])
        elif "date" in match.lower():
            items_string += InsertItemString3.replace("{{{Item}}}", match)
        else:
            items_string += InsertItemString.replace("{{{Item}}}", match)
    
    file_path = os.path.join(table_folder, "Insert.cshtml")
    with open(file_path, 'w') as file:
        file.write(
            InsertString.replace("{{{NAME}}}", table_name).replace("{{{ITEMS}}}", items_string).replace("{{{WebApplication}}}", project_name)
        )

def create_update():
    items_string = ""
    for match in matches:
        if "Id" == match:
            continue
        if match.endswith("Id"):
            items_string += UpdateItemString2.replace("{{{Item}}}", match[:-2])
        elif "date" in match.lower():
            items_string += UpdateItemString3.replace("{{{Item}}}", match)
        else:
            items_string += UpdateItemString.replace("{{{Item}}}", match)
    
    file_path = os.path.join(table_folder, "Update.cshtml")
    with open(file_path, 'w') as file:
        file.write(
            UpdateString.replace("{{{NAME}}}", table_name).replace("{{{ITEMS}}}", items_string).replace("{{{WebApplication}}}", project_name)
        )

def create_main_index():
    items_string = ""
    for cs_file in cs_files:
        if "\Tb" not in cs_file:
            continue
        items_string += MainIndexStringItem.replace("{{{Item}}}", cs_file.split("\\")[-1][:-3])

    os.makedirs(main_path, exist_ok=True)
    file_path = os.path.join(main_path, "Index.cshtml")
    with open(file_path, 'w') as file:
        file.write(
            MainIndexString.replace("{{{ITEMS}}}", items_string)
        )

directory_path = input("Enter Path: ")
cs_files = glob.glob(os.path.join(directory_path, 'Models\Entity\*.cs'))

controllers_path = os.path.join(directory_path, "Controllers")
views_path = os.path.join(directory_path, "Views")
shared_path = os.path.join(views_path, "Shared")
main_path = os.path.join(views_path, "Main")

os.makedirs(shared_path, exist_ok=True)
with open(os.path.join(shared_path, "_Layout.cshtml"), 'w') as file:
    file.write(SharedLayoutString)

with open(os.path.join(directory_path, "Web.config"), 'r') as file:
    EntityName = re.findall('<add name="(.+?)" connectionString="', file.read())[-1]

for cs_file in cs_files:
    # if cs_file.endswith("\Entity\Model1.Context.cs") or cs_file.endswith("\Entity\sysdiagram.cs"):
    #     continue
    if "\Tb" not in cs_file:
        continue
    with open(cs_file, 'r') as file:
        content = file.read()
    
    matches = re.findall("        public .+? (.+?) { get; set; }", content)
    matches = list(filter(lambda x: " " not in x, matches))
    if not matches:
        continue

    print(cs_file, matches)
    project_name = re.findall("namespace (.+?)\.", content)[0]
    table_name = re.findall("public partial class (.+?)\n", content)[0]
    table_folder = os.path.join(views_path, table_name)
    os.makedirs(table_folder, exist_ok=True)

    create_controller()
    create_index()
    create_delete()
    create_insert()
    create_update()

create_main_controller()
create_main_index()