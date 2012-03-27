toolname = 'flowmax'
version = '042910-alpha'
env = Environment(TARFLAGS="-c -z")
env.Tar('_'.join([toolname,version])+'.tgz', [env.Glob('*.py'), 'pkg', 'conf', 'run.sh', 'README'])
