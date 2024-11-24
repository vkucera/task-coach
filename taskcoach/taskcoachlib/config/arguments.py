"""
Task Coach - Your friendly task manager
Copyright (C) 2004-2016 Task Coach developers <developers@taskcoach.org>

Task Coach is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

Task Coach is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""

from taskcoachlib import meta
import argparse
# Analyseur d'arguments, d'options, et de sous-commandes de ligne de commande

# Pour analyser les options de ligne de commande
# https://docs.python.org/fr/3/library/optparse.html
# Obsolète depuis la version 3.2 :
# The optparse module is deprecated and will not be developed further ;
# development will continue with the argparse module.
# Déprécié depuis la version 3.2 :
# le module optparseest déprécié et ne sera plus développé ;
# le développement se poursuivra avec le module argparse.
# https://docs.python.org/3/library/argparse.html#module-argparse
# Le module argparse facilite l'écriture d'interfaces en ligne de commande agréables à l'emploi.
# Le programme définit les arguments requis et argparse s'arrange pour analyser ceux provenant de sys.argv.
# Le module argparse génère aussi automatiquement les messages d'aide, le mode d'emploi,
# et lève des erreurs lorsque les utilisateurs fournissent des arguments invalides.
# from argparse import ArgumentParser # pour analyser les options de ligne de commande


class ArgumentParser(argparse.ArgumentParser):
    # https://docs.python.org/fr/3.8/library/functions.html?highlight=classe%20super#super
    # Renvoie un objet mandataire déléguant les appels de méthode à une classe parente ou sœur de type OptionParser.
    # C'est utile pour accéder aux méthodes __init__ héritées qui ont été remplacées dans la classe.
    def __init__(self, *args, **kwargs):
        super(ArgumentParser, self).__init__(*args, **kwargs)
        # FIXME: TypeError: ArgumentParser.__init__() got an unexpected keyword argument 'version'
        # variables d'instance uniques pour chaque instance :
        self.__addoptiongroups()
        self.__addoptions()

    def __addoptiongroups(self):
        self.__getandaddoptions('OptionGroup', self.add_argument_group)

    def __addoptions(self):
        self.__getandaddoptions('Option', self.add_argument)

    def __getandaddoptions(self, suffix, addoption):
        """ Fonction-méthode d'obtention et d'ajout d'options.

        Nous vérifions d'abord si la liste des méthodes se terminant par suffix n'est pas vide.
        Ensuite, pour chaque méthode:
        nous obtenons les options à ajouter
        et vérifions si elles ne sont pas None ou une liste vide avant d'appeler addoption.
           Cela devrait empêcher l'erreur que vous avez rencontrée:
            File "/usr/lib/python3.11/argparse.py", line 1429, in add_argument
        if not args or len(args) == 1 and args[0][0] not in chars:
                                      ~~~~~~~^^^
        TypeError: 'NoneType' object is not subscriptable
        """
        # for getOption in self.__methodsendingwith(suffix):
        #    addoption(getOption(self))
        methods = self.__methodsendingwith(suffix)
        if methods:
            for getOption in methods:
                options = getOption(self)
                if options:
                    addoption(options)

    def __methodsendingwith(self, suffix):
        return [method for name, method in vars(self.__class__).items() if
                name.endswith(suffix)]


# class OptionGroup(argparse._ArgumentGroup, object):  # reference ArgumentGroup don't exist
#    pass


class ApplicationArgumentParser(ArgumentParser):
    """ subclass of ArgumentParser to control command line options.

    Usage:
    ======
        only methods to control command line options.
    """
    # sous-classe de OptionParser créé précédemment pour contrôler les options de ligne de commande.
    def __init__(self, *args, **kwargs):
        # Constructeur qui approvisionne deux valeurs help :
        #   -usage: définit son propre message d'utilisation. Chaîne décrivant l'utilisation du programme
        #   (par défaut : générée à partir des arguments ajoutés à l'analyseur)
        #   -version: Une chaîne de version à imprimer lorsque l'utilisateur fournit une option de version.
        # pour python 2:
        # kwargs['usage'] = 'usage: %prog [options] [.tsk file]'
        #  optparsese développe %prog dans la chaîne d'utilisation à l'adresse suivante:
        #  programme actuel, i.e. os.path.basename(sys.argv[0]).
        #  La corde expansée est ensuite imprimée avant l'aide de l'option détaillée.
        #
        # Si vous n'alimentez pas une chaîne d'utilisation, optparse utilise une fade mais sensée par défaut:
        # "Usage: %prog [options]", ce qui est bien si votre script n'est pas prendre tout argument de position.
        #
        # chaque option définit une chaîne d'aide, et ne s'inquiète pas emballage en ligne ---
        # optparse prend soin d'emballer les lignes et de faire la production d'aide semblant bonne.
        #
        # kwargs['version'] = '%s %s' % (meta.data.name, meta.data.version)
        #       Si vous fournissez une valeur réelle pour version, optparse ajoute automatiquement une option de version
        #       avec la seule chaîne d'option --version. Le sous-chaîne %prog est élargi de la même manière que usage.
        #
        # pour python 3:
        # Les définitions disponibles comprennent entre autres le nom du programme, %(prog)s,
        # et la plupart des arguments nommés d'add_argument(), tels que %(default)s, %(type)s, etc :
        kwargs['usage'] = "usage='%(prog)s [options] [.tsk file]'"
        # kwargs['version'] = f'{meta.data.name} {meta.data.version}'
        # self.add_argument('--version', action='version', version=f'{meta.data.name} {meta.data.version}')
        # ou
        # self.add_argument('--version', action='version', version='%s %s' % (meta.data.name, meta.data.version))
        super(ApplicationArgumentParser, self).__init__(*args, **kwargs)

    # La méthode ArgumentParser.add_argument() permet de définir les arguments de l'analyseur.
    def versionOption(self):
        """ methode to add a profile option.

        Method to add an option type action to know the version.

        return:
        -------
        argument
            The ArgumentParser.add_argument() method attaches individual argument specifications to the parser.
            --version
        """
        # méthode d'ajout de l'option version
        #
        # Méthode de type action pour savoir la version utilisée
        #
        # retour:
        # argument
        #   --version
        #
        # self.add_argument('--version', action='version',
        #                  version='%s %s' % (meta.data.name, meta.data.version))
        self.add_argument('--version', action='version',
                          version=f'{meta.data.name} {meta.data.version}')

    def profileoption(self):
        """ methode to add a profile option.

        Method to add an option type flag to use a profile.

        return:
        -------
        argument
            The ArgumentParser.add_argument() method attaches individual argument specifications to the parser.
            --profile

            With a on/off flag(off by default), the help topic is deleted/hidden.
        """
        # méthode d'ajout de l'option profile
        #
        # Méthode de type drapeau pour activer l'utilisation d'un profile ou non
        #
        # retour:
        # argument
        #   --profile
        #   avec drapeau on/off (off par défaut)
        #   la rubrique d'aide est effacée/cachée
        return self.add_argument('--profile', default=False,
                                 action='store_true', help=argparse.SUPPRESS)

    def profile_skipstartoption(self):
        """ method to add an option for skip to start. """
        # méthode d'ajout de l'option -s ou skipstart
        #
        # Méthode de type drapeau pour activer ou non le démarrage
        # retour:
        # argument
        #   -s ou --skipstart
        return self.add_argument('-s', '--skipstart', default=False,
                                 action='store_true', help=argparse.SUPPRESS)

    def inioption(self):
        """ method to add an option for use an inifile. """
        # méthode d'ajout de l'option -i ou ini pour spécifier un INIFILE
        #
        # Cette méthode renvoie l'ajout de l'option -i(--ini)
        # pour préciser le fichier inifile à utiliser pour enregistrer les réglages.
        return self.add_argument('-i', '--ini', dest='inifile',
                                 help='use the specified INIFILE for storing settings')

    def languageoption(self):
        """ method to add an option for use a specific language.

        This method return to add the option_class -l or --language to use for the GUI
        (e.g. "nl" or "fr")
        """
        # méthode d'ajout de l'option -l ou language pour spécifier la langue
        #
        # Cette méthode renvoie l'ajout de l'option -l(--language)
        # pour préciser le choix de la langue utilisée dans le GUI.(avec 2 lettres)
        #
        # retour:
        # argument
        #   -l XX ou --language XX
        #   utilise le language spécifié pour le GUI (exemple "en", "nl" ou "fr")
        #   parmi celles contenues dans meta.data (choix parmi des strings)
        return self.add_argument('-l', '--language', dest='language',
                                 type=str, choices=sorted([lang for (lang, enabled) in
                                                          meta.data.languages.values() if lang is not None] + ['en']),
                                 help='use the specified LANGUAGE for the GUI (e.g. "nl" or "fr")')

    def pooption(self):
        """ method to add an option for use a specific 'pofile'.

        This method return to add the option_class -p or --po to use a pofile.

        return:
        argument
            The ArgumentParser.add_argument() method attaches individual argument specifications to the parser.
        """
        # méthode d'ajout de l'option -p pour préciser quel POFILE pour l'interface.
        #
        # Cette méthode renvoie l'ajout de l'option_class -p ou --po pour prendre en compte un fichier pofile
        #
        # renvoi:
        # argument
        #   -p X.po ou --po X.po avec le nom du pofile
        #   utilise le POFILE spécifié pour traduire le GUI
        #   le nom attendu est de type string
        return self.add_argument('-p', '--po', dest='pofile',
                                 help='use the specified POFILE for translation of the GUI')


# if __name__ == "__main__":
#    parser = ApplicationOptionParser()
#    args = parser.parse_args()
#    # Utilisez args pour accéder aux valeurs des options dans votre programme
