//
//  TaskDetailsController-iPad.m
//  TaskCoach
//
//  Created by Jérôme Laheurte on 14/06/10.
//  Copyright 2010 Jérôme Laheurte. All rights reserved.
//

#import "TaskCoachAppDelegate.h"
#import "TaskDetailsControlleriPad.h"
#import "TaskCategoryPickerController.h"
#import "TaskDetailsEffortsBase.h"
#import "TaskDetailsRecurrenceControlleriPad.h"
#import "DateUtils.h"
#import "i18n.h"

#import "SimpleDatePicker.h"

#import "CDTask.h"
#import "CDTask+Addons.h"
#import "CDDomainObject+Addons.h"

@interface TaskDetailsControlleriPad ()

- (void)onSaveDescription:(UIBarButtonItem *)button;
- (void)refreshButtons;
- (void)saveTask;

@end

@implementation TaskDetailsControlleriPad

@synthesize subject;
@synthesize description;
@synthesize startDateButton;
@synthesize dueDateButton;
@synthesize completionDateButton;
@synthesize reminderDateButton;
@synthesize priorityLabel;
@synthesize recurrenceButton;
@synthesize effortButton;

@synthesize taskCatCtrl;
@synthesize taskEffortCtrl;

- initWithTask:(CDTask *)theTask
{
	if (self = [super initWithNibName:@"TaskDetailsControlleriPad" bundle:[NSBundle mainBundle]])
	{
		task = [theTask retain];

		datePicker = [[SimpleDatePicker alloc] initWithTarget:self action:@selector(onNullDate)];
	}

	return self;
}

- (void)viewDidLoad
{
	[super viewDidLoad];

	self.navigationItem.title = task.name;

	self.subject.text = task.name;
	self.description.text = task.longDescription;

	[self refreshButtons];

	if (![task.name length])
		[subject becomeFirstResponder];

	[taskCatCtrl setTask:task];
	[taskEffortCtrl setTask:task];
	[taskEffortCtrl updateButton:effortButton];
}

- (void)viewDidUnload
{
	self.subject = nil;
	self.description = nil;
	self.startDateButton = nil;
	self.dueDateButton = nil;
	self.completionDateButton = nil;
	self.reminderDateButton = nil;
	self.priorityLabel = nil;
	self.recurrenceButton = nil;
	self.effortButton = nil;
	self.taskCatCtrl = nil;
	self.taskEffortCtrl = nil;
}

- (void)dealloc
{
	[self viewDidUnload];

	[datePicker release];

	[super dealloc];
}

- (BOOL)shouldAutorotateToInterfaceOrientation:(UIInterfaceOrientation)interfaceOrientation
{
	if (popoverCtrl)
	{
		[popoverCtrl dismissPopoverAnimated:YES];
	}

    return YES;
}

- (void)didRotateFromInterfaceOrientation:(UIInterfaceOrientation)fromInterfaceOrientation
{
	if (popoverCtrl)
	{
		UIButton *button;

		if (dateName)
		{
			if ([dateName isEqualToString:@"startDate"])
				button = startDateButton;
			else if ([dateName isEqualToString:@"dueDate"])
				button = dueDateButton;
			else if ([dateName isEqualToString:@"completionDate"])
				button = completionDateButton;
			else
				button = reminderDateButton;
		}
		else
			button = recurrenceButton;

		[popoverCtrl presentPopoverFromRect:button.frame inView:self.view permittedArrowDirections:UIPopoverArrowDirectionAny animated:YES];
	}
}

- (void)refreshButtons
{
	if (task.startDate)
		[self.startDateButton setTitle:[[TimeUtils instance] stringFromDate:task.startDate] forState:UIControlStateNormal];
	else
		[self.startDateButton setTitle:_("None") forState:UIControlStateNormal];
	
	if (task.dueDate)
		[self.dueDateButton setTitle:[[TimeUtils instance] stringFromDate:task.dueDate] forState:UIControlStateNormal];
	else
		[self.dueDateButton setTitle:_("None") forState:UIControlStateNormal];
	
	if (task.completionDate)
		[self.completionDateButton setTitle:[[TimeUtils instance] stringFromDate:task.completionDate] forState:UIControlStateNormal];
	else
		[self.completionDateButton setTitle:_("None") forState:UIControlStateNormal];
	
	if (task.reminderDate)
		[self.reminderDateButton setTitle:[[TimeUtils instance] stringFromDate:task.reminderDate] forState:UIControlStateNormal];
	else
		[self.reminderDateButton setTitle:_("None") forState:UIControlStateNormal];

	priorityLabel.text = [NSString stringWithFormat:_("Priority: %@"), task.priority];
}

- (void)saveTask
{
	[task markDirty];
	NSError *error;
	if (![getManagedObjectContext() save:&error])
	{
		UIAlertView *alert = [[UIAlertView alloc] initWithTitle:_("Error") message:_("Could not save task.") delegate:self cancelButtonTitle:_("OK") otherButtonTitles:nil];
		[alert show];
		[alert release];
	}
}

#pragma mark Actions

- (IBAction)onClickDate:(UIButton *)button
{
	if (button == startDateButton)
	{
		dateName = @"startDate";
	}
	else if (button == dueDateButton)
	{
		dateName = @"dueDate";
	}
	else if (button == completionDateButton)
	{
		dateName = @"completionDate";
	}
	else if (button == reminderDateButton)
	{
		dateName = @"reminderDate";
	}
	else
	{
		assert(0);
	}

	datePicker.date = [task valueForKey:dateName];

	popoverCtrl = [[UIPopoverController alloc] initWithContentViewController:datePicker];
	[popoverCtrl setPopoverContentSize:CGSizeMake(320, 281) animated:NO];
	[popoverCtrl presentPopoverFromRect:button.frame inView:self.view permittedArrowDirections:UIPopoverArrowDirectionAny animated:YES];
	popoverCtrl.delegate = self;
}

- (void)onNullDate
{
	[task setValue:nil forKey:dateName];
	dateName = nil;
	[self saveTask];

	[popoverCtrl dismissPopoverAnimated:YES]; // This doesn't call popoverControllerDidDismissPopover
	[popoverCtrl release];
	popoverCtrl = nil;

	[self refreshButtons];
}

- (IBAction)incPriority:(UIButton *)button
{
	task.priority = [NSNumber numberWithInt:[task.priority intValue] + 1];
	[self saveTask];
	[self refreshButtons];
}

- (IBAction)decPriority:(UIButton *)button
{
	NSInteger p =[task.priority intValue];
	if (p > 0)
	{
		task.priority = [NSNumber numberWithInt:p - 1];
		[self saveTask];
		[self refreshButtons];
	}
}

- (IBAction)onClickEffort:(UIButton *)button
{
	[taskEffortCtrl onTrack:button];
}

- (IBAction)onClickRecurrence:(UIButton *)button
{
	TaskDetailsRecurrenceControlleriPad *ctrl = [[TaskDetailsRecurrenceControlleriPad alloc] initWithTask:task];
	popoverCtrl = [[UIPopoverController alloc] initWithContentViewController:ctrl];
	[popoverCtrl setPopoverContentSize:CGSizeMake(284, 141)];
	[popoverCtrl presentPopoverFromRect:button.frame inView:self.view permittedArrowDirections:UIPopoverArrowDirectionAny animated:YES];
	[ctrl release];
}

#pragma mark UIPopoverControllerDelegate

- (void)popoverControllerDidDismissPopover:(UIPopoverController *)popoverController
{
	if (dateName)
	{
		[task setValue:datePicker.date forKey:dateName];
		dateName = nil;
		[self saveTask];
	}

	[popoverCtrl release];
	popoverCtrl = nil;

	[self refreshButtons];
}

#pragma mark UITextFieldDelegate protocol

- (BOOL)textFieldShouldReturn:(UITextField *)textField
{
	[textField resignFirstResponder];
	return NO;
}

- (void)textFieldDidEndEditing:(UITextField *)textField
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
	
	[self saveTask];
	
	self.navigationItem.title = task.name;
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
	[self saveTask];
}

@end
