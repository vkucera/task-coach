//
//  StringChoiceController.m
//  TaskCoach
//
//  Created by Jérôme Laheurte on 14/01/09.
//  Copyright 2009 Jérôme Laheurte. See COPYING for details.
//

#import "StringChoiceController.h"

@implementation StringChoiceController

@synthesize textField;

- initWithPlaceholder:(NSString *)thePlaceholder target:(id)theTarget action:(SEL)theAction
{
	if (self = [super initWithNibName:@"StringChoice" bundle:[NSBundle mainBundle]])
	{
		placeholder = [thePlaceholder retain];
		target = theTarget;
		action = theAction;
	}

	return self;
}

- (void)viewDidLoad
{
	textField.placeholder = placeholder;
	[textField becomeFirstResponder];
}

- (void)viewDidUnload
{
	self.textField = nil;
}

- (void)dealloc
{
	[placeholder release];

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
		// XXXTODO: alert
		return NO;
	}
}

@end
