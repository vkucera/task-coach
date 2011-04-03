//
//  TaskHeaderView.m
//  Task Coach
//
//  Created by Jérôme Laheurte on 03/04/11.
//  Copyright 2011 __MyCompanyName__. All rights reserved.
//

#import "TaskHeaderView.h"
#import "CDTask+Addons.h"
#import "i18n.h"

@implementation TaskHeaderView

- (id)initWithCoder:(NSCoder *)aDecoder
{
    if ((self = [super initWithCoder:aDecoder]))
    {
        bgImage = [[UIImage imageNamed:@"headerbg"] retain];
    }

    return self;
}

- (void)dealloc
{
    [bgImage release];

    [super dealloc];
}

- (void)setStyle:(NSInteger)style
{
    switch (style)
    {
        case TASKSTATUS_TRACKING:
            textLabel.text = _("Tracked");
            textLabel.textColor = [[[UIColor alloc] initWithRed:0.7 green:0 blue:0 alpha:1] autorelease];
            imageView.image = [UIImage imageNamed:@"ledclock"];
            break;
        case TASKSTATUS_OVERDUE:
            textLabel.text = _("Overdue");
            textLabel.textColor = [UIColor redColor];
            imageView.image = [UIImage imageNamed:@"folderred"];
            break;
        case TASKSTATUS_DUESOON:
            textLabel.text = _("Due soon");
            textLabel.textColor = [UIColor orangeColor];
            imageView.image = [UIImage imageNamed:@"folderorange"];
            break;
        case TASKSTATUS_STARTED:
            textLabel.text = _("Started");
            textLabel.textColor = [UIColor blueColor];
            imageView.image = [UIImage imageNamed:@"folderblue"];
            break;
        case TASKSTATUS_NOTSTARTED:
            textLabel.text = _("Not started");
            textLabel.textColor = [UIColor grayColor];
            imageView.image = [UIImage imageNamed:@"foldergrey"];
            break;
        case TASKSTATUS_COMPLETED:
            textLabel.text = _("Completed");
            textLabel.textColor = [UIColor greenColor];
            imageView.image = [UIImage imageNamed:@"foldergreen"];
            break;
    }
}

#pragma mark - Drawing

- (void)drawRect:(CGRect)rect
{
	CGContextRef context = UIGraphicsGetCurrentContext();
	CGContextSaveGState(context);
	CGContextClipToRect(context, rect);
	CGContextDrawTiledImage(context, CGRectMake(0, 0, 1, 41), bgImage.CGImage);
	CGContextRestoreGState(context);
	
	[super drawRect:rect];
}

@end
