from cx_Freeze import setup, Executable

# Dependencies are automatically detected, but it might need
# fine tuning.
build_options = {'packages': ["keyring", "pyperclip", "onetimepass", "subprocess", "re"], 'excludes': []}

base = 'Console'

executables = [
    Executable(script = 'totp_saml.py', base = base, target_name = 'totp_saml')
]

setup(name='saml2aws-totp',
      version = '1.0',
      description = '',
      options = {'build_exe': build_options},
      executables = executables)
