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
@synthesize priorityValue;
@synthesize incPriorityButton;
@synthesize decPriorityButton;

- initWithTask:(CDTask *)theTask parent:(TaskDetailsController *)parent
{
	if ((self = [super initWithNibName:@"TaskDetailsGeneral" bundle:[NSBundle mainBundle]]))
	{
		task = [theTask retain];
		parentCtrl = parent;

        if ([self respondsToSelector:@selector(edgesForExtendedLayout)])
            self.edgesForExtendedLayout = UIRectEdgeNone;
	}

	return self;
}

- (void)viewDidLoad
{
	[super viewDidLoad];

	self.subject.text = task.name;
	self.description.text = task.longDescription;

	self.descriptionLabel.text = _("Description");
	self.categoriesButton.titleLabel.text = _("Categories");
	self.priorityValue.text = [NSString stringWithFormat:_("%@"), task.priority];

	if (![task.name length])
		[subject becomeFirstResponder];
}

- (void)viewDidUnload
{
	self.subject = nil;
	self.descriptionLabel = nil;
	self.description = nil;
	self.categoriesButton = nil;
	self.priorityValue = nil;
	self.incPriorityButton = nil;
	self.decPriorityButton = nil;
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

- (IBAction)changePriority:(UIButton *)button
{
	if (button == incPriorityButton)
		task.priority = [NSNumber numberWithInt:[task.priority intValue] + 1];
	else
		task.priority = [NSNumber numberWithInt:[task.priority intValue] - 1];

	self.priorityValue.text = [NSString stringWithFormat:_("%@"), task.priority];
	
	[task markDirty];
	[task save];
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

- (void)onEditingPriorityDone:(id)sender
{
    [priorityValue resignFirstResponder];
}

#pragma mark UITextFieldDelegate protocol

- (BOOL)textFieldShouldReturn:(UITextField *)textField
{
	[textField resignFirstResponder];
	return NO;
}

- (void)textFieldDidBeginEditing:(UITextField *)textField
{
    if (textField == priorityValue)
    {
        self.navigationItem.rightBarButtonItem = [[[UIBarButtonItem alloc] initWithBarButtonSystemItem:UIBarButtonSystemItemDone target:self action:@selector(onEditingPriorityDone:)] autorelease];
    }
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
    }
    else if (textField == priorityValue)
    {
        task.priority = [NSNumber numberWithInt:[textField.text intValue]];
        self.navigationItem.rightBarButtonItem = nil;
    }
	
	[task markDirty];
	[task save];
	
	self.navigationItem.title = task.name;
}

- (BOOL)textFieldShouldClear:(UITextField *)textField

{
    if (textField == priorityValue)
    {
        priorityValue.text = @"0";
        return NO;
    }
    else
    {
        return YES;
    }
}

#pragma mark UITextViewDelegate protocol

- (BOOL)textViewShouldBeginEditing:(UITextView *)textView
{
	UIBarButtonItem *button = [[UIBarButtonItem alloc] initWithBarButtonSystemItem:UIBarButtonSystemItemSave target:self action:@selector(onSaveDescription:)];
	self.navigationItem.rightBarButtonItem = button;
	[button release];
	
	CGPoint p = description.frame.origin;
	p.x = 0;
	p.y -= 5;

	[(UIScrollView *)self.view setContentOffset:p animated:YES];
	
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
	[task save];

	[(UIScrollView *)self.view setContentOffset:CGPointMake(0, 0) animated:YES];
}

@end
