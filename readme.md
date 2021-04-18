[![Gitpod Ready-to-Code](https://img.shields.io/badge/Gitpod-Ready--to--Code-blue?logo=gitpod)](https://gitpod.io/#https://Jehazekel/info2602Project.git) 

[![Run on Repl.it](https://repl.it/badge/github.com/Jehazekel/info2602Project)](https://repl.it/Jehazekel/info2602Project)

# Flask App Template
You can use this app to get started with a basic flask application. If you are building out a project and need to deploy its recommeded to use the [flask mvc template](https://github.com/uwidcit/flaskmvc)

# Creating & Linking your own github repository
Git is used to perform source control. It helps teams manage code bases and merge together their contributions.
Github is a free Git server for developers to host their git repositories.

When the project is launched on gitpod (by clicking the gitpod button above), it will already be linked to this starter github repository. To link it to a new repository you need to first run the following command.

```
rm - rf .git
```
Now you can initialize a new git workspace by executing the following.


```
git init
```

Next, create your respository on github by following this [link](https://github.com/new). Give it a name and click on the green "Create Repository" button below.
The next page would give you instructions on how to link the repository to an existing workspace.

Copy the command which looks like.

```
git remote add origin https://github.com/<username>/<reponame>.git
```
Paste and run the command in gitpod.

Your workspace should now be linked to your repository

# Pushing changes to Git
Now the workspace is linked with a git repository it will track all the changes you make to its files.
Run the following command to select which files will be **staged** (tracked for changes)

```
git stage *
```

This will stage all files in the workspace.
Then You prepare the changes to be sent to the repository by making a **commit**. You must supply a custom commit message when making commits.
Run the following command

```
git commit -m "first commit"
```

Finally you can send your changes to the repository by performing a **push**.

```
git push -u origin master
```
At this point you want to **delete** this workspace from the [gitpod dashboard](https://gitpod.io/workspaces/) so that you can create a new workspace from your new repository. 

To create a new workspace go to your repository on github and prepend "https://gitpod.io/#" to the address in the url bar then navigate to that address.

![Editing Address bar](/img/url.png)

Your new workspace should be created on gipod. This will allow you to use the version control UI in gitpod to push changes to github.
