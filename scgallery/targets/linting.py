####################################################
# Target Setup
####################################################
def setup(chip):
    '''
    Dummy target to use for linting
    '''

    chip.set('option', 'mode', 'sim')

    chip.set('asic', 'logiclib', 'lint_target')
