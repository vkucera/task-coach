//
//  StringChoiceController.m
//  TaskCoach
//
//  Created by Jérôme Laheurte on 14/01/09.
//  Copyright 2009 Jérôme Laheurte. See COPYING for details.
//

#import "StringChoiceController.h"
#import "i18n.h"

@implementation StringChoiceController

@synthesize textField;

- initWithPlaceholder:(NSString *)thePlaceholder text:(NSString *)theText target:(id)theTarget action:(SEL)theAction
{
	if (self = [super initWithNibName:@"StringChoice" bundle:[NSBundle mainBundle]])
	{
		placeholder = [thePlaceholder retain];
		text = [theText retain];

		target = theTarget;
		action = theAction;
	}

	return self;
}

- (void)viewDidLoad
{
	textField.placeholder = placeholder;
	textField.text = text;

	[textField becomeFirstResponder];
}

- (void)viewDidUnload
{
	self.textField = nil;
}

- (void)dealloc
{
	[self viewDidUnload];

	[placeholder release];
	[text release];

    [super dealloc];
}

- (IBAction)onCancel:(UIButton *)button
{
	[target performSelector:action withObject:nil];
}

- (BOOL)textFieldShouldReturn:(UITextField *)field
{
	if ([field.text length])
	{
		[target performSelector:action withObject:field.text];
		return YES;
	}
	else
	{
		UIAlertView *alert = [[UIAlertView alloc] initWithTitle:_("Error") message:_("Empty text.") delegate:self cancelButtonTitle:_("OK") otherButtonTitles:nil];
		[alert show];
		[alert release];

		return NO;
	}
}

@end
