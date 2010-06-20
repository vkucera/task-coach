    //
//  NewCategoryiPad.m
//  TaskCoach
//
//  Created by Jérôme Laheurte on 20/06/10.
//  Copyright 2010 Jérôme Laheurte. All rights reserved.
//

#import "NewCategoryiPad.h"
#import "i18n.h"

@implementation NewCategoryiPad

@synthesize categoryName;
@synthesize okButton;

- initWithString:(NSString *)string target:(id)theTarget action:(SEL)theAction
{
	if (self = [super initWithNibName:@"NewCategoryiPad" bundle:[NSBundle mainBundle]])
	{
		target = theTarget;
		action = theAction;

		name = [string copy];
	}

	return self;
}

- (BOOL)shouldAutorotateToInterfaceOrientation:(UIInterfaceOrientation)interfaceOrientation
{
    return YES;
}

- (void)viewDidLoad
{
	[super viewDidLoad];

	categoryName.placeholder = _("Category name");
	categoryName.text = name;
	[okButton setTitle:_("OK") forState:UIControlStateNormal];
	[categoryName becomeFirstResponder];
}

- (void)viewDidUnload
{
    [super viewDidUnload];

	self.categoryName = nil;
	self.okButton = nil;
}

- (void)dealloc
{
	[self viewDidUnload];

	[name release];

    [super dealloc];
}

#pragma mark Actions

- (IBAction)onClickOK:(UIButton *)button
{
	[target performSelector:action withObject:categoryName.text];
}

#pragma mark UITextFieldDelegate

- (BOOL)textFieldShouldReturn:(UITextField *)textField
{
	[target performSelector:action withObject:categoryName.text];

	return NO;
}

@end
