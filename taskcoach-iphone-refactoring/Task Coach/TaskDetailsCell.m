//
//  TaskDetailsCell.m
//  Task Coach
//
//  Created by Jérôme Laheurte on 09/04/11.
//  Copyright 2011 __MyCompanyName__. All rights reserved.
//

#import "TaskDetailsCell.h"
#import "CDTask+Addons.h"
#import "CDDomainObject+Addons.h"
#import "DateUtils.h"
#import "i18n.h"

static UIImage *_imageChecked = NULL;
static UIImage *_imageUnchecked = NULL;

@implementation TaskDetailsCell

- (void)dealloc
{
    if (callback)
        Block_release(callback);

    [theTask release];

    [super dealloc];
}

- (void)setTask:(CDTask *)task callback:(void (^)(id))theCallback
{
    if (!_imageChecked)
    {
        _imageChecked = [[UIImage imageNamed:@"checked"] retain];
        _imageUnchecked = [[UIImage imageNamed:@"unchecked"] retain];
    }

    if ([[task objectID] isEqual:[theTask objectID]])
        return;

    if (callback)
        Block_release(callback);
    callback = Block_copy(theCallback);

    subject.text = task.name;
    completionButton.image = ([task completionDate]) ? _imageChecked : _imageUnchecked;
    [completionButton setCallback:^(id sender) {
        [task toggleCompletion];
    }];

    if ([task currentEffort])
    {
        [trackButton setTitle:_("Stop tracking") forState:UIControlStateNormal];
    }
    else
    {
        [trackButton setTitle:_("Start tracking") forState:UIControlStateNormal];
    }
    [trackButton setBackgroundImage:[[UIImage imageNamed:@"redButton"] stretchableImageWithLeftCapWidth:12.0 topCapHeight:0.0] forState:UIControlStateNormal];
    [trackButton setBackgroundImage:[[UIImage imageNamed:@"whiteButton"] stretchableImageWithLeftCapWidth:12.0 topCapHeight:0.0] forState:UIControlStateHighlighted];

    [trackButton setCallback:^(id sender) {
        if ([task currentEffort])
            [task stopTracking];
        else
            [task startTracking];

        callback(self);
    }];

    [theTask release];
    theTask = task;

    [datesTable selectRowAtIndexPath:[NSIndexPath indexPathForRow:0 inSection:0] animated:NO scrollPosition:UITableViewScrollPositionNone];
    if (theTask.startDate)
        [datePicker setDate:theTask.startDate];
    else
        [datePicker setDate:[NSDate date]];
}

- (void)editSubject
{
    [subject becomeFirstResponder];
}

#pragma mark - UITextFieldDelegate

- (void)textFieldDidEndEditing:(UITextField *)textField
{
    theTask.name = subject.text;
    [theTask save];

    [subject resignFirstResponder];
}

#pragma mark - Date picker

- (IBAction)onChangeDate:(id)sender
{
    NSIndexPath *indexPath = [datesTable indexPathForSelectedRow];
    if (indexPath)
    {
        switch (indexPath.row)
        {
            case 0:
                theTask.startDate = datePicker.date;
                break;
            case 1:
                theTask.dueDate = datePicker.date;
                break;
        }
        
        [theTask save];
    }

    [datesTable reloadRowsAtIndexPaths:[NSArray arrayWithObject:indexPath] withRowAnimation:UITableViewRowAnimationNone];
    [datesTable selectRowAtIndexPath:indexPath animated:NO scrollPosition:UITableViewScrollPositionNone];
}

#pragma mark - Table view data source

- (NSInteger)numberOfSectionsInTableView:(UITableView *)tableView
{
    return 1;
}

- (NSInteger)tableView:(UITableView *)tableView numberOfRowsInSection:(NSInteger)section
{
    return 2;
}

- (UITableViewCell *)tableView:(UITableView *)tableView cellForRowAtIndexPath:(NSIndexPath *)indexPath
{
    UITableViewCell *cell = [datesTable dequeueReusableCellWithIdentifier:@"Cell"];
    if (!cell)
        cell = [[[UITableViewCell alloc] initWithStyle:UITableViewCellStyleDefault reuseIdentifier:@"Cell"] autorelease];

    switch (indexPath.row)
    {
        case 0:
            if (theTask.startDate)
                cell.textLabel.text = [NSString stringWithFormat:_("Start %@"), [[UserTimeUtils instance] stringFromDate:theTask.startDate]];
            else
                cell.textLabel.text = _("No start date.");
            break;
        case 1:
            if (theTask.dueDate)
                cell.textLabel.text = [NSString stringWithFormat:_("Due %@"), [[UserTimeUtils instance] stringFromDate:theTask.dueDate]];
            else
                cell.textLabel.text = _("No due date.");
            break;
    }

    return cell;
}

#pragma mark - Table view delegate

- (void)tableView:(UITableView *)tableView didSelectRowAtIndexPath:(NSIndexPath *)indexPath
{
    NSDate *theDate;
    switch (indexPath.row)
    {
        case 0:
            theDate = theTask.startDate;
            break;
        case 1:
            theDate = theTask.dueDate;
            break;
    }
    
    if (theDate)
        [datePicker setDate:theDate animated:NO];
    else
        [datePicker setDate:[NSDate date] animated:NO];
}

@end
