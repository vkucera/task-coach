//
//  StringChoiceAlert.m
//  TaskCoach
//
//  Created by Jérôme Laheurte on 14/01/09.
//  Copyright 2009 Jérôme Laheurte. See COPYING for details.
//

#import "StringChoiceAlert.h"
#import "i18n.h"

@implementation StringChoiceAlert

- initWithPlaceholder:(NSString *)thePlaceholder text:(NSString *)theText target:(id)theTarget action:(SEL)theAction
{
	if ((self = [super initWithTitle:@"" message:@"" delegate:self cancelButtonTitle:_("Cancel") otherButtonTitles:_("OK"), nil]))
	{
        self.alertViewStyle = UIAlertViewStylePlainTextInput;
        [self textFieldAtIndex:0].text = theText;
        [self textFieldAtIndex:0].placeholder = thePlaceholder;

		target = theTarget;
		action = theAction;
	}

	return self;
}

#pragma mark UIAlertViewDelegate

- (void)alertView:(UIAlertView *)alertView didDismissWithButtonIndex:(NSInteger)buttonIndex
{
	switch (buttonIndex)
	{
		case 0:
			[target performSelector:action withObject:nil];
			break;
		case 1:
			[target performSelector:action withObject:[[self textFieldAtIndex:0] text]];
			break;
	}
}

@end
