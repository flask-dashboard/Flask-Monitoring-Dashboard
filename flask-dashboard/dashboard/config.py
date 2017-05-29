import configparser
import os


class Config(object):
    """
        The settings can be changed by setting up a config file. For an example of a config file, see
         config.cfg in the main-directory. 
    """

    def __init__(self):
        """
            Sets the default values for the project
        """
        self.version = '1.0'
        self.link = 'dashboard'
        self.database_name = 'sqlite:///flask-dashboard.db'
        self.group = None

    def from_file(self, config_file):
        """
            The config_file must at least contains the following variables in section 'dashboard':
            APP_VERSION: the version of the app that you use. Updating the version helps in 
                showing differences in execution times of a function over a period of time.
            CUSTOM_LINK: The dashboard can be visited at localhost:5000/{{CUSTOM_LINK}}.
            DATABASE: Suppose you have multiple projects where you're working on and want to 
                separate the results. Then you can specify different database_names, such that the 
                result of each project is stored in its own database.
            GROUP_BY: applies as a filter to sort the results based on this group_by-tag.
            
            Since updating the version in the config-file when updating code isn't very useful, it
            is a better idea to provide the location of the git-folder. From the git-folder. The 
            version automatically retrieved by reading the commit-id (hashed value):
            GIT = If you're using git, then it is easier to set the location to the .git-folder, 
                The location is relative to the config-file.
            
            
            :param config_file: a string pointing to the location of the config-file
        """

        parser = configparser.RawConfigParser()
        try:
            parser.read(config_file)
            if parser.has_option('dashboard', 'APP_VERSION'):
                self.version = parser.get('dashboard', 'APP_VERSION')
            if parser.has_option('dashboard', 'CUSTOM_LINK'):
                self.link = parser.get('dashboard', 'CUSTOM_LINK')
            if parser.has_option('dashboard', 'DATABASE'):
                self.database_name = parser.get('dashboard', 'DATABASE')
            if parser.has_option('dashboard', 'GROUP_BY'):
                self.group = parser.get('dashboard', 'GROUP_BY')
            # When the option git is selected, it overrides the given version
            if parser.has_option('dashboard', 'GIT'):
                git = parser.get('dashboard', 'GIT')
                try:
                    # location to git-folder
                    directory = str(config_file.rsplit('/', 1)[0]) + git
                    # current hash can be found in the link in HEAD-file in git-folder
                    # The file is specified by: 'ref: <location>'
                    git_file = (open(os.path.join(directory, 'HEAD')).read().rsplit(': ', 1)[1]).rstrip()
                    # read the git-version
                    self.version = open(directory + '/' + git_file).read()
                except IOError:
                    print("Error reading one of the files to retrieve the current git-version.")
                    raise
        except configparser.Error:
            raise
