//
//  AlertPrompt.m
//  Prompt
//
//  Created by Jeff LaMarche on 2/26/09.

#import "AlertPrompt.h"
#import "i18n.h"

@implementation AlertPrompt

- (id)initWithTitle:(NSString *)title message:(NSString *)message cancelAction:(void (^)(void))theCancelAction confirmAction:(void (^)(NSString *))theConfirmAction secure:(BOOL)secure
{
    if ((self = [super initWithTitle:title message:message delegate:self cancelButtonTitle:_("Cancel") otherButtonTitles:_("OK"), nil]))
    {
        UITextField *theTextField = [[UITextField alloc] initWithFrame:CGRectMake(12.0, 45.0, 260.0, 25.0)]; 
        [theTextField setBackgroundColor:[UIColor whiteColor]]; 
		theTextField.secureTextEntry = secure;

        [self addSubview:theTextField];
        textField = theTextField;

        cancelAction = Block_copy(theCancelAction);
        confirmAction = Block_copy(theConfirmAction);
    }

    return self;
}

- (void)show
{
    [textField becomeFirstResponder];
    [super show];
}

- (NSString *)enteredText
{
    return textField.text;
}

- (void)dealloc
{
    [textField release];

    Block_release(cancelAction);
    Block_release(confirmAction);

    [super dealloc];
}

#pragma mark - UIAlertViewDelegate

- (void)alertView:(UIAlertView *)alertView clickedButtonAtIndex:(NSInteger)buttonIndex
{
    switch (buttonIndex)
    {
        case 0:
            cancelAction();
            break;
        case 1:
            confirmAction(textField.text);
            break;
    }
}

@end