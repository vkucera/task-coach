//
//  TaskDetailsGeneral.m
//  TaskCoach
//
//  Created by Jérôme Laheurte on 16/05/10.
//  Copyright 2010 Jérôme Laheurte. All rights reserved.
//

#import "TaskCoachAppDelegate.h"

#import "TaskDetailsGeneral.h"
#import "TaskCategoryPickerController.h"

#import "CDTask.h"
#import "CDDomainObject+Addons.h"

#import "i18n.h"

@interface TaskDetailsGeneral ()

- (void)onSaveDescription:(UIBarButtonItem *)button;

@end;

@implementation TaskDetailsGeneral

@synthesize subject;
@synthesize descriptionLabel;
@synthesize description;
@synthesize categoriesButton;
@synthesize priorityLabel;
@synthesize priorityField;

- initWithTask:(CDTask *)theTask parent:(TaskDetailsController *)parent
{
	if (self = [super initWithNibName:@"TaskDetailsGeneral" bundle:[NSBundle mainBundle]])
	{
		task = [theTask retain];
		parentCtrl = parent;
	}

	return self;
}

- (void)viewDidLoad
{
	[super viewDidLoad];

	self.subject.text = task.name;
	self.description.text = task.longDescription;
	self.priorityField.text = [NSString stringWithFormat:@"%@", task.priority];

	self.descriptionLabel.text = _("Description");
	self.categoriesButton.titleLabel.text = _("Categories");
	self.priorityLabel.text = _("Priority:");

	if (![task.name length])
		[subject becomeFirstResponder];
}

- (void)viewDidUnload
{
	self.subject = nil;
	self.descriptionLabel = nil;
	self.description = nil;
	self.categoriesButton = nil;
}

- (void)dealloc
{
	[self viewDidUnload];

	[task release];
	[super dealloc];
}

- (BOOL)shouldAutorotateToInterfaceOrientation:(UIInterfaceOrientation)toInterfaceOrientation
{
	return YES;
}

- (UINavigationItem *)navigationItem
{
	return parentCtrl.navigationItem;
}

- (IBAction)onCategoriesClick:(UIButton *)btn
{
	TaskCategoryPickerController *categoryPicker = [[TaskCategoryPickerController alloc] initWithTask:task];
	[parentCtrl.navigationController pushViewController:categoryPicker animated:YES];
	[categoryPicker release];
}

#pragma mark UITextFieldDelegate protocol

- (BOOL)textFieldShouldReturn:(UITextField *)textField
{
	if (textField == subject)
	{
		[textField resignFirstResponder];
		return NO;
	}
	else
		return YES;
}

- (void)textFieldDidEndEditing:(UITextField *)textField
{
	if (textField == subject)
	{
		if ([textField.text length])
		{
			task.name = textField.text;
		}
		else
		{
			task.name = _("New task");
			textField.text = task.name;
		}
		
		[task markDirty];
		NSError *error;
		if (![getManagedObjectContext() save:&error])
		{
			UIAlertView *alert = [[UIAlertView alloc] initWithTitle:_("Error") message:_("Could not save task.") delegate:self cancelButtonTitle:_("OK") otherButtonTitles:nil];
			[alert show];
			[alert release];
		}
		
		self.navigationItem.title = task.name;
	}
}

- (BOOL)textField:(UITextField *)textField shouldChangeCharactersInRange:(NSRange)range replacementString:(NSString *)string
{
	if (textField == priorityField)
	{
		NSString *newValue = [textField.text stringByReplacingCharactersInRange:range withString:string];
		
		if ([newValue length])
		{
			task.priority = [NSNumber numberWithInt:atoi([newValue UTF8String])];
		}
		else
		{
			task.priority = [NSNumber numberWithInt:0];
		}
		
		[task markDirty];
		
		NSError *error;
		if (![getManagedObjectContext() save:&error])
		{
			UIAlertView *alert = [[UIAlertView alloc] initWithTitle:_("Error") message:_("Could not save task.") delegate:self cancelButtonTitle:_("OK") otherButtonTitles:nil];
			[alert show];
			[alert release];
		}
	}
	
	return YES;
}

#pragma mark UITextViewDelegate protocol

- (BOOL)textViewShouldBeginEditing:(UITextView *)textView
{
	UIBarButtonItem *button = [[UIBarButtonItem alloc] initWithBarButtonSystemItem:UIBarButtonSystemItemSave target:self action:@selector(onSaveDescription:)];
	self.navigationItem.rightBarButtonItem = button;
	[button release];
	
	return YES;
}

- (void)textViewDidEndEditing:(UITextView *)textView
{
	self.navigationItem.rightBarButtonItem = nil;
	[self onSaveDescription:nil];
}

- (void)onSaveDescription:(UIBarButtonItem *)button
{
	[description resignFirstResponder];

	task.longDescription = description.text;
	[task markDirty];
	NSError *error;
	if (![getManagedObjectContext() save:&error])
	{
		UIAlertView *alert = [[UIAlertView alloc] initWithTitle:_("Error") message:_("Could not save task.") delegate:self cancelButtonTitle:_("OK") otherButtonTitles:nil];
		[alert show];
		[alert release];
	}
}

@end
