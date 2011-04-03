//
//  TaskTableView.m
//  Task Coach
//
//  Created by Jérôme Laheurte on 03/04/11.
//  Copyright 2011 __MyCompanyName__. All rights reserved.
//

#import "TaskTableView.h"
#import "Task_CoachAppDelegate.h"
#import "CDDomainObject+Addons.h"
#import "SmartAlertView.h"
#import "Configuration.h"
#import "CDTask+Addons.h"
#import "CDCategory.h"
#import "String+Utils.h"
#import "TaskHeaderViewFactory.h"
#import "i18n.h"

@interface TaskTableView ()

- (void)configureCell:(UITableViewCell *)cell forTask:(CDTask *)task;

@end

@implementation TaskTableView

- (void)dealloc
{
    [self viewDidUnload];

    [super dealloc];
}

#pragma mark - View lifecycle

- (void)viewDidLoad
{
    [super viewDidLoad];

    NSFetchRequest *req = [[NSFetchRequest alloc] init];
    [req setEntity:[NSEntityDescription entityForName:@"CDTask" inManagedObjectContext:getManagedObjectContext()]];
    [req setPredicate:[NSPredicate predicateWithFormat:@"status != %d AND list=%@", STATUS_DELETED, [Configuration instance].currentList]];

    NSMutableArray *sorting = [[NSMutableArray alloc] initWithCapacity:3];
    NSSortDescriptor *des;
    
    des = [[NSSortDescriptor alloc] initWithKey:[Configuration instance].groupingName ascending:![Configuration instance].revertGrouping];
    [sorting addObject:des];
    [des release];

    if ([Configuration instance].grouping != GROUPING_START)
    {
        des = [[NSSortDescriptor alloc] initWithKey:@"startDate" ascending:YES];
        [sorting addObject:des];
        [des release];
    }

    des = [[NSSortDescriptor alloc] initWithKey:@"name" ascending:YES];
    [sorting addObject:des];
    [des release];

    [req setSortDescriptors:sorting];
    [sorting release];

    resultsCtrl = [[NSFetchedResultsController alloc] initWithFetchRequest:req managedObjectContext:getManagedObjectContext() sectionNameKeyPath:[Configuration instance].groupingName cacheName:nil];
    [req release];

    NSError *error;
    if (![resultsCtrl performFetch:&error])
    {
        SmartAlertView *alert = [[SmartAlertView alloc] initWithTitle:_("Error") message:[NSString stringWithFormat:_("Could not fetch tasks: %@"), [error localizedDescription]] cancelButtonTitle:_("OK") cancelAction:^(void) {
            // Nothing
        }];
        [alert show];
        [alert release];
    }
}

- (void)viewDidUnload
{
    [super viewDidUnload];

    [resultsCtrl release];
    resultsCtrl = nil;
}

- (BOOL)shouldAutorotateToInterfaceOrientation:(UIInterfaceOrientation)interfaceOrientation
{
    return YES;
}

#pragma mark - Table view data source

- (NSInteger)numberOfSectionsInTableView:(UITableView *)tableView
{
    return [[resultsCtrl sections] count];
}

- (NSString *)tableView:(UITableView *)tableView titleForHeaderInSection:(NSInteger)section
{
    id <NSFetchedResultsSectionInfo> info = [[resultsCtrl sections] objectAtIndex:section];

    switch ([Configuration instance].grouping)
    {
        case GROUPING_PRIORITY:
            return [info name];
        default:
        {
            struct tm cdate;
            (void)strptime([[info name] UTF8String], "%Y-%m-%d %H:%M:%S %z", &cdate);
            NSDate *date = [NSDate dateWithTimeIntervalSince1970:mktime(&cdate)];
            NSDateFormatter *fmt = [[[NSDateFormatter alloc] init] autorelease];

            [fmt setDateStyle:NSDateFormatterMediumStyle];
            [fmt setTimeStyle:NSDateFormatterMediumStyle];
            return [fmt stringFromDate:date];
        }
    }

    return nil;
}

- (UIView *)tableView:(UITableView *)tableView viewForHeaderInSection:(NSInteger)section
{
    if ([Configuration instance].grouping == GROUPING_STATUS)
    {
        TaskHeaderView *view = [[TaskHeaderViewFactory instance] create];
        [view setStyle:[[[[resultsCtrl sections] objectAtIndex:section] name] intValue]];
        return view;
    }

    return nil;
}

- (CGFloat)tableView:(UITableView *)tableView heightForHeaderInSection:(NSInteger)section
{
    return 41;
}

- (NSInteger)tableView:(UITableView *)tableView numberOfRowsInSection:(NSInteger)section
{
    id <NSFetchedResultsSectionInfo> info = [[resultsCtrl sections] objectAtIndex:section];
    return [info numberOfObjects];
}

- (UITableViewCell *)tableView:(UITableView *)tableView cellForRowAtIndexPath:(NSIndexPath *)indexPath
{
    static NSString *CellIdentifier = @"Cell";
    
    UITableViewCell *cell = [tableView dequeueReusableCellWithIdentifier:CellIdentifier];
    if (cell == nil)
    {
        cell = [[[UITableViewCell alloc] initWithStyle:UITableViewCellStyleSubtitle reuseIdentifier:CellIdentifier] autorelease];
    }

    CDTask *task = [resultsCtrl objectAtIndexPath:indexPath];
    [self configureCell:cell forTask:task];
    
    return cell;
}

/*
// Override to support conditional editing of the table view.
- (BOOL)tableView:(UITableView *)tableView canEditRowAtIndexPath:(NSIndexPath *)indexPath
{
    // Return NO if you do not want the specified item to be editable.
    return YES;
}
*/

/*
// Override to support editing the table view.
- (void)tableView:(UITableView *)tableView commitEditingStyle:(UITableViewCellEditingStyle)editingStyle forRowAtIndexPath:(NSIndexPath *)indexPath
{
    if (editingStyle == UITableViewCellEditingStyleDelete) {
        // Delete the row from the data source
        [tableView deleteRowsAtIndexPaths:[NSArray arrayWithObject:indexPath] withRowAnimation:UITableViewRowAnimationFade];
    }   
    else if (editingStyle == UITableViewCellEditingStyleInsert) {
        // Create a new instance of the appropriate class, insert it into the array, and add a new row to the table view
    }   
}
*/

/*
// Override to support rearranging the table view.
- (void)tableView:(UITableView *)tableView moveRowAtIndexPath:(NSIndexPath *)fromIndexPath toIndexPath:(NSIndexPath *)toIndexPath
{
}
*/

/*
// Override to support conditional rearranging of the table view.
- (BOOL)tableView:(UITableView *)tableView canMoveRowAtIndexPath:(NSIndexPath *)indexPath
{
    // Return NO if you do not want the item to be re-orderable.
    return YES;
}
*/

#pragma mark - Table view delegate

- (void)tableView:(UITableView *)tableView didSelectRowAtIndexPath:(NSIndexPath *)indexPath
{
    // Navigation logic may go here. Create and push another view controller.
    /*
     <#DetailViewController#> *detailViewController = [[<#DetailViewController#> alloc] initWithNibName:@"<#Nib name#>" bundle:nil];
     // ...
     // Pass the selected object to the new view controller.
     [self.navigationController pushViewController:detailViewController animated:YES];
     [detailViewController release];
     */
}

#pragma mark - Task cells

- (void)configureCell:(UITableViewCell *)cell forTask:(CDTask *)task
{
    cell.textLabel.text = task.name;

    switch ([task.dateStatus intValue])
    {
        case TASKSTATUS_TRACKING:
            cell.textLabel.textColor = [[[UIColor alloc] initWithRed:0.7 green:0 blue:0 alpha:1.0] autorelease];
            break;
        case TASKSTATUS_OVERDUE:
            cell.textLabel.textColor = [UIColor redColor];
            break;
        case TASKSTATUS_DUESOON:
            cell.textLabel.textColor = [UIColor orangeColor];
            break;
        case TASKSTATUS_STARTED:
            cell.textLabel.textColor = [UIColor blueColor];
            break;
        case TASKSTATUS_NOTSTARTED:
            cell.textLabel.textColor = [UIColor grayColor];
            break;
        case TASKSTATUS_COMPLETED:
            cell.textLabel.textColor = [UIColor greenColor];
            break;
        default:
            cell.textLabel.textColor = [UIColor blackColor];
            break;
    }

    NSMutableArray *categoryNames = [[NSMutableArray alloc] init];
    for (CDCategory *category in task.categories)
        [categoryNames addObject:category.name];
    cell.detailTextLabel.text = [@", " stringByJoiningStrings:categoryNames];
    [categoryNames release];
}

@end
