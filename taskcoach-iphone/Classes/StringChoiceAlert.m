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
	if ((self = [super initWithTitle:@"" message:@"\n\n" delegate:self cancelButtonTitle:_("Cancel") okButtonTitle:_("OK")]))
	{
		textField.placeholder = thePlaceholder;
		textField.text = theText;
		textField.secureTextEntry = NO;

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
			[target performSelector:action withObject:textField.text];
			break;
	}
}

@end
