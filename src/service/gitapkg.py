import git

URL = 'https://github.com/apkgbot/agda-packages.git'
g = git.cmd.Git('client')

class GitApkg:

  def clone(self):
    git.Git('').clone(URL)

  def pull(self):
    g.pull()