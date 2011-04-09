//
//  TaskCell.m
//  Task Coach
//
//  Created by Jérôme Laheurte on 03/04/11.
//  Copyright 2011 __MyCompanyName__. All rights reserved.
//

#import "TaskCell.h"

#import "Task_CoachAppDelegate.h"
#import "CDTask+Addons.h"
#import "String+Utils.h"
#import "CDCategory.h"
#import "CDEffort.h"
#import "ImageButton.h"
#import "DateUtils.h"

static UIImage *_imageChecked = NULL;
static UIImage *_imageUnchecked = NULL;

@implementation TaskCell

- (void)dealloc
{
    [super dealloc];
}

- (void)setTask:(CDTask *)task
{
    if (!_imageChecked)
    {
        _imageChecked = [[UIImage imageNamed:@"checked"] retain];
        _imageUnchecked = [[UIImage imageNamed:@"unchecked"] retain];
    }

    mainLabel.text = task.name;
    checkView.image = ([task completionDate]) ? _imageChecked : _imageUnchecked;
    rightLabel.text = @"";

    [checkView setCallback:^(id sender) {
        [task toggleCompletion];
    }];

    switch ([task.dateStatus intValue])
    {
        case TASKSTATUS_TRACKING:
        {
            mainLabel.textColor = [[[UIColor alloc] initWithRed:0.7 green:0 blue:0 alpha:1.0] autorelease];
            CDEffort *effort = [task currentEffort];
            if (effort && !(effort.ended)) // Hum
            {
                NSTimeInterval elapsed = [[NSDate date] timeIntervalSinceDate:effort.started];
                rightLabel.text = formatTime((int)elapsed);
            }
            break;
        }
        case TASKSTATUS_OVERDUE:
            mainLabel.textColor = [UIColor redColor];
            break;
        case TASKSTATUS_DUESOON:
            mainLabel.textColor = [UIColor orangeColor];
            break;
        case TASKSTATUS_STARTED:
            mainLabel.textColor = [UIColor blueColor];
            break;
        case TASKSTATUS_NOTSTARTED:
            mainLabel.textColor = [UIColor grayColor];
            break;
        case TASKSTATUS_COMPLETED:
            mainLabel.textColor = [UIColor greenColor];
            checkView.image = _imageChecked;
            break;
        default:
            mainLabel.textColor = [UIColor blackColor];
            break;
    }
    
    NSMutableArray *categoryNames = [[NSMutableArray alloc] init];
    for (CDCategory *category in task.categories)
        [categoryNames addObject:category.name];
    leftLabel.text = [@", " stringByJoiningStrings:categoryNames];
    [categoryNames release];
}

@end
